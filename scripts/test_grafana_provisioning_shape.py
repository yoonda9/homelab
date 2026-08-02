"""Shape tests for the Grafana provisioning path (Step 4a).

Step 4's demo is "open Grafana and see panels populate". Two repo-side claims sat
between the provisioned files and a rendered panel, and this file exists because
**only one of them survived measurement**. Both were measured against the pinned
image itself, offline, before a line of the fix was written
(`logs/calibration-step04a-grafana-identity.py` / `.log`,
`logs/calibration-step04a-delivered-tree-boots.py` / `.log`):

  * **THE MODES CLAIM IS FALSE, AND THE GUARD IS WRITTEN AGAINST WHAT REPLACED
    IT.** The claim was that `tasks/main.yml`'s `0750` grafana dirs and `0640`
    renders are unreadable to the container because `grafana/grafana:13.1.0` runs
    as uid 472. It runs as **uid 472, gid 0** — `Config.User='472'`, and a uid
    with no explicit gid takes gid 0 — so `root`-GROUP bits answer for it. Row
    B1: the delivered tree (0750 dirs / 0640 files, root:root, both mounts `:ro`)
    is READABLE as 472:0; row D1: a real server booted on that exact tree
    provisions the datasource AND lands `dashboard.grafana.app/dashboards/
    homelab-overview` in its store with no permission line in the log. The
    `0644` on `prometheus.yml` next door is NOT a precedent to copy blindly —
    row A2 measured why it was needed there and not here: `prom/prometheus`
    runs `65534:65534`, which matches neither owner nor group, where grafana's
    gid 0 does. Traefik's renders stay `0640` for the same family of reason.

    So the modes are correct as delivered and this file does not demand a
    number. It pins the PROPERTY that makes them correct — the delivered
    owner/group/mode must grant read (and traverse, for dirs) to the identity
    `uid 472, gid 0` — which `0750`/`0640` root:root satisfies through the group
    bit and `0755`/`0644` satisfies through the other bit. A guard that demanded
    `0755` would have forbidden the real answer, which is the failure this repo
    has already hit once.

    That property has a COMPANION and it is in a different file, so it is
    checked in a different file: the identity only stays `472:0` while the
    compose service declines to override it. Row B4 — the same delivered tree
    read as `472:472` — is DENIED. `test_grafana_service_keeps_the_root_group`
    is therefore load-bearing for the mode checks, not decoration.

  * **THE UID CLAIM IS TRUE.** `grafana-datasource.yml.j2` provisioned a
    datasource NAMED `Prometheus` with no `uid:`, and every panel and target of
    `files/grafana-homelab-dashboard.json` references `uid: "Prometheus"`. Row
    C1 read the server's own store: the generated uid is **`PBFA97CFB590B2093`**,
    not `Prometheus`. A name is not a uid and the reference does not resolve.
    Row C2 pins the fix: with `uid: Prometheus` declared, the stored uid is
    `Prometheus` exactly, so the two sides agree BY CONSTRUCTION rather than by
    coincidence. (What is INFERRED and not measured: that an unresolvable uid
    renders as "Datasource not found" rather than silently falling back to the
    `isDefault: true` datasource. The fix does not rest on which it is — the
    reference resolves either way once the uids agree — so the inference is
    recorded, not relied on.)

The load-bearing check here is CROSS-FILE and it is
`test_delivered_dashboards_reference_the_provisioned_uid`: a check that reads
only the datasource, or only the dashboard, cannot see a disagreement between
them. Its dashboard side is an INVENTORY over the files the role actually
delivers into the mounted dashboards dir, so the dashboards that Step 4b and 4c
add cannot silently skip it, and `test_dashboard_delivery_inventory_is_complete`
closes the other direction — a dashboard JSON added to `files/` and never
delivered.

Dual-mode (module-level `test_*() -> bool` + `main() -> int`), stdlib only, per
the repo rule that the gate pythons have no PyYAML (mem-1782133401-4307).
Per mem-1781892715-142d every regex anchors on the inner value, not a section
opener, and every reader FAILS on a file it cannot read rather than skipping.
The real gate is the standalone exit code.
"""

import json
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLE = REPO_ROOT / "ansible" / "roles" / "docker_host"
TASKS = ROLE / "tasks" / "main.yml"
TEMPLATES = ROLE / "templates"
FILES = ROLE / "files"
COMPOSE = TEMPLATES / "compose.yml.j2"
DATASOURCE_TPL = TEMPLATES / "grafana-datasource.yml.j2"
DASHBOARDS_TPL = TEMPLATES / "grafana-dashboards.yml.j2"

# The identity `grafana/grafana:13.1.0` runs as, MEASURED from the image itself
# (calibration row A1: Config.User='472' -> `id` reports uid=472(grafana)
# gid=0(root) groups=0(root)). Both numbers are load-bearing and the gid is the
# one the Planner's D1 missed: it is why root-GROUP bits answer for this
# container and why the delivered 0750/0640 root:root tree is readable at all.
GRAFANA_UID = 472
GRAFANA_GIDS = {0}

# The datasource uids a dashboard may reference WITHOUT any provisioning file
# declaring them. Not a pattern and not a guess: read off the running server's
# own `/api/frontend/settings` (`logs/calibration-step04a-builtin-datasources.log`),
# which is the map the UI resolves a reference against — exactly these three
# carry `meta.builtIn: True`, beside the provisioned `Prometheus`. The image's JS
# bundle also mentions `-- Public --`; the SERVER does not offer it, so it is not
# here. Bounded by what was measured rather than by the wider thing that was seen.
#
# This exists because every dashboard EXPORTED from Grafana carries the built-in
# annotation `{"type":"grafana","uid":"-- Grafana --"}`, so without it the
# cross-file check below would redden on an ordinary export — the "guard forbids
# the real answer" failure this repo has already hit once, and the one Step 4b
# and 4c would have hit first.
GRAFANA_BUILTIN_DATASOURCE_UIDS = frozenset({"-- Grafana --", "-- Mixed --", "-- Dashboard --"})

# WHERE A DASHBOARD DECLARES A QUERY, and what a query variable's `query` is when
# it is NOT one. Read off the two JSONs this role delivers (`$.panels[i]
# .targets[j].expr`, `$.templating.list[i].definition`, `$.templating.list[i]
# .query.query`) and off Grafana's dashboard schema for the carriers those two do
# not happen to use today — a collapsed row's child panels
# (`$.panels[i].panels[j].targets[k].expr`), an annotation query
# (`$.annotations.list[i].expr`, and `.target.expr` in the older spelling), and a
# variable query in its legacy STRING form.
#
# THE NON-QUERY VARIABLE TYPES ARE THE POINT OF THE SECOND SET. A `custom`
# variable's `query` is `"a,b,c"` — a value list, not PromQL — and a `constant`'s
# is a literal. Reading those as expressions would be the same mistake as reading
# a description as one, one field further along, so the type decides and the
# types are enumerated rather than assumed.
GRAFANA_PROMETHEUS_DATASOURCE_TYPE = "prometheus"
GRAFANA_TARGET_EXPR_KEY = "expr"
GRAFANA_QUERY_VARIABLE_TYPE = "query"
GRAFANA_VARIABLE_QUERY_KEYS = ("query", "definition")
GRAFANA_NON_QUERY_VARIABLE_TYPES = frozenset(
    {"adhoc", "constant", "custom", "datasource", "interval", "textbox", "system"})

# TWO MORE KEYS OF A `templating.list[]` ENTRY THAT DECIDE WHAT THE OPERATOR SEES,
# both read out of grafana/grafana:13.1.0 itself by the sourcemap method the rest
# of this file uses (`logs/calibration-step05d-rework-r2-regex-hide.py` / `.log`,
# 20/20; the review that found them measured the same two independently in
# `logs/critic-step05d-grafana-regex-hide.sh`).
#
# `regex` IS NOT A COSMETIC FILTER. `metricNamesToVariableValues` compiles it
# under JS truthiness (`if (variableRegEx)`, so `""` — what this tree delivers —
# is inert and ANY non-empty string is live), then for every value the query
# returned: a value the pattern does not match is DROPPED (`if (!matches.length)
# continue`) and a capture group REWRITES it (`text = value = firstMatch[1]`, and
# the named `value`/`text` groups do the same). `stringToJsRegex` anchors a bare
# string as `^…$`. So the list the operator picks from is not the list the query
# yielded, and the two harms have opposite shapes — CT 111 silently missing, or
# every `{id="$guest"}` panel permanently empty because the values became `110`.
# `regexApplyTo` only chooses WHICH of text/value the pattern is tested against;
# the drop and the rewrites are downstream of both branches, so it cannot make a
# non-empty regex inert and nothing here has to read it (calibration R4).
#
# `hide` IS AN ENUM AND ONLY ONE OF ITS FOUR VALUES REMOVES THE CONTROL.
# `VariableValueSelectWrapper` returns null — no picker at all — exactly on
# `hide === VariableHide.hideVariable`; `hideLabel` (1) drops the LABEL and leaves
# the picker, and `inControlsMenu` (3) moves it. So the refusal is the single
# value 2, in its v1 numeric spelling and the v2 schema's string one, and a check
# that refused every non-zero `hide` would forbid two legitimate dashboards
# (calibration H1/H3/H5, and B4/B5 of `logs/red-step05d-rework-r2.py`).
GRAFANA_VARIABLE_REGEX_KEY = "regex"
GRAFANA_VARIABLE_HIDE_KEY = "hide"
GRAFANA_HIDE_VARIABLE_VALUES = (2, "hideVariable")
# JS truthiness for the JSON scalars a dashboard field can hold: these are the
# values `if (variableRegEx)` skips the whole filter for. MEASURED AGAINST NODE
# ITSELF rather than reasoned about: every candidate a dashboard field can hold
# (`false`/`true`/`0`/`1`/`""`/`"false"`/`" "`/`null`/`0.0`/`[]`/`{}`) was put
# through `!(!x)` in node v22 and through `not in` this tuple, and the two agree
# on all twelve (`logs/calibration-step05d-rework-r3-includeall.py` B1-B12). The
# two rows that matter are the ones a Python `is True` would get wrong in
# opposite directions: `"false"` is a TRUE flag to Grafana and `0` is not one.
GRAFANA_FALSY_VALUES = (None, "", 0, False)

# A THIRD KEY OF THE SAME ENTRY, AND UNLIKE `regex` AND `hide` IT IS NOT A
# PROPERTY OF THE VARIABLE ALONE — it is fatal or inert depending on what the
# PANELS wrote, so it is checked where the matchers are read and not in
# `_pve_container_drop_down`. Both keys let one variable interpolate MORE THAN
# ONE value at once, and the whole chain was read out of grafana/grafana:13.1.0's
# own sourcesContent (`logs/calibration-step05d-rework-r3-includeall.py`, 33/33,
# offline, nothing started; the review that found `includeAll` measured the same
# links independently in `logs/critic-step05d-r2-includeall.py`):
#
#   * `dashboard-scene/utils/variables.ts` carries BOTH keys into the running
#     variable, and one of them RAW: `defaultToAll: Boolean(variable.includeAll)`
#     but `isMulti: variable.multi` (A1/A2). `sceneInterpolator.formatValue` then
#     hands the datasource `{multi: state.isMulti, includeAll: state.includeAll}`
#     with no normalisation (A4), and `@grafana/prometheus`' `escaping.mjs` opens
#     the array branch on `if (!variable.multi && !variable.includeAll)` (A5). So
#     the gate is JS truthiness on the JSON scalar — hence `GRAFANA_FALSY_VALUES`
#     above and not an `is True`.
#   * `includeAll` BREAKS ON LOAD, with nobody having chosen anything: the
#     delivered entry ships `"current": {}`, the transform starts `value` at `''`
#     (A9), `findOptionMatchingCurrent` fails, and `getDefaultSingleState`'s FIRST
#     branch is `if (defaultToAll) return ALL_VARIABLE_VALUE` (A8). `getValue()`
#     then returns `options.map(o => o.value)` — the ARRAY (A10) — which
#     `escaping.mjs` joins into `"(" + … + ")"` (A7).
#   * `multi` DOES NOT break on load, and it is refused anyway. The array branch
#     returns `escapedValues[0]` for a single selection (A6), so one ticked
#     container interpolates the bare id exactly as today (engine C5); the harm
#     arrives on the operator's SECOND tick, in one click, with no file edited.
#   * AN `allValue` IS NOT AN ESCAPE. `CustomAllValue.formatter` returns its
#     string RAW (A11), so `allValue: "lxc/.*"` is pasted in unescaped and selects
#     nothing under `=` (engine C6) — a third spelling of the same harm.
GRAFANA_VARIABLE_ALTERNATING_KEYS = ("includeAll", "multi")

# A FOURTH KEY OF THE SAME ENTRY, LIVE INSIDE THE ACCEPT REGION ROUND 3 OPENED.
# Round 3 refused `includeAll`/`multi` only against a LITERAL matcher, because
# `{id=~"$guest"}` with All is an ordinary working dashboard — and `allValue` is
# read exactly there, in the half that stayed accepted. One field of the variable
# editor on that blessed state, `allValue: ".*"`, makes all thirteen
# per-container panels graph the WHOLE CLUSTER on load with both containers still
# in the picker: never empty, always wrong, which this file prices above the
# merely-blank class. Round 3 priced the key as "reachable only through
# `includeAll`/`multi` and cannot rescue them" — true of the FLAT refusal it did
# not take, false of the narrow rule it did (`mem-1785555524-400d`: a key is
# priced against a SHAPE, and when the shape changes the pricing has expired).
# The chain is re-measured in `logs/calibration-step05d-rework-r4-allvalue.py`
# (28/28, zero FAILs, offline out of grafana/grafana:13.1.0's own sourcesContent,
# plus `prom/prometheus:v3.12.0`; the "25/26 with B5 the declared MISS" this
# sentence carried in round 4 was the count of ANOTHER hat's harness,
# `logs/critic-step05d-r3-allvalue.py` at 19/20 — a reader checking the bound got
# a number its own evidence contradicts, which is the review's F2):
#
#   * `getValue()` reads `allValue` INSIDE `hasAllValue()` and ABOVE the
#     `options.map(o => o.value)` round 3's whole alternation chain starts from
#     (A1), so with this key set there is no array and no alternation.
#   * `CustomAllValue.formatter` ends `return this._value` (A11) and
#     `sceneInterpolator.formatValue` SHORT-CIRCUITS on it — `return
#     sceneInterpolator(context, value.formatter(...))` (A12). The datasource's
#     `interpolateQueryExpr` is never reached: no Prometheus escaping, no
#     operator awareness, the string pasted raw and re-interpolated. That is why
#     the refusal cannot be a (variable, operator) pair the way round 3's is.
#   * THE KEY, NOT THE PAIR, and this is the one thing the measurement changed.
#     Everything visible from the picker says the harm needs `includeAll`: the
#     All OPTION is added only under it (A3) and validation resets a stray All to
#     `options[0]` (A4). But `updateFromUrl` calls `changeValueTo($__all)` with
#     NO `includeAll` condition, sets `skipNextValidation` while the variable is
#     inactive — which is what a dashboard opened from a link is — and
#     `interceptStateUpdateAfterValidation` puts the URL's value BACK over that
#     reset (A5/A6). A URL carrying the allValue STRING is mapped onto All too
#     (A7). So a file with `allValue` and no `includeAll` is one shared link away
#     from the same harm, and a rule over the pair would call it inert.
#   * ENGINE, on the round's own fixture: `{id=~".*"}` returns the node, the VM
#     and the storage beside the containers (C2), `{id=~"node/.*"}` the node
#     alone (C3) — and `{id=~"lxc/.*"}` returns exactly the two containers (C4),
#     which is the REAL dashboard this refusal costs. That price is scored as D1
#     of `logs/red-step05d-rework-r4.py` rather than denied.
#
# THE SHAPE IS THE `regex` REFUSAL'S, for the `regex` refusal's reason: deciding
# what an arbitrary JS regex admits is the "cannot say" this file answers with a
# refusal everywhere else, the escape is one field of the variable editor, and
# widening it later is additive.
GRAFANA_VARIABLE_ALL_VALUE_KEY = "allValue"

# The ONE state immune to all three keys — a panel that REPEATS over the
# drop-down — is exempted rather than refused, and the measurement that says it
# is safe is in `_panel_repeats_over`.

# EVERY KEY OF THE DROP-DOWN ENTRY THIS FILE HAS PRICED, and the row prints the
# ones it has not. Three consecutive reviews found a defect in a key nobody had
# looked at — `regex` and `hide` in round 1, `includeAll` in round 3 — and each
# round answered the keys it was handed and left the rest unexamined. Both
# reviews called the entry "twelve keys"; it delivers FOURTEEN (calibration D0,
# counted rather than repeated), which is how easy the class is to lose track of.
# So the remaining keys were measured rather than argued about, all of them out
# of the same pinned image:
#
#   * `type` / `query` / `definition` — read by `_pve_container_drop_down`.
#   * `regex` / `hide` — refused there (round 2).
#   * `includeAll` / `multi` — refused against a LITERAL matcher by clause 2's
#     second half (round 3).
#   * `allValue` — refused wherever the drop-down is named, WHATEVER the operator
#     (round 4). Round 3 priced it here as "reachable only through
#     `includeAll`/`multi` and cannot rescue them", which was measured against
#     the flat refusal that was NOT taken: under the narrow rule that shipped,
#     `includeAll` stays accepted whenever the panels spell `=~`, and that is
#     precisely where an `allValue` is read. See
#     `GRAFANA_VARIABLE_ALL_VALUE_KEY`. THE GENERAL FORM OF THAT MISTAKE IS THE
#     ONE THIS LIST EXISTS TO STOP MAKING: a key is priced against a SHAPE, so
#     every "unreachable" here has to be read against the region the rule
#     ACCEPTS, not the region it refuses — a printer for keys OUTSIDE the set
#     cannot catch a key inside it that was priced against the wrong shape.
#   * `name` — read by clauses 2 and 3, as the reference the panels interpolate.
#   * `datasource` — priced by OTHER rows of this file: a `templating.list[]`
#     entry is a datasource carrier for the uid row and the type row, so a
#     variable pointed at a dead datasource is already refused there.
#   * `refresh` (round 2's B9) and `options` (calibration D2) — the saved option
#     list is overwritten from the query on load, so neither can freeze it.
#   * `sort` — `sortVariableValues` is `sortBy`/`reverse` in every branch and
#     never a filter, so it reorders the list and cannot drop a container (D1).
#   * `current` — a saved selection matching no option falls through to
#     `getDefaultSingleState` (D5), so a stale one cannot pin the drop-down, and
#     re-read against round 4's URL door it holds: `skipNextValidation` is set by
#     `updateFromUrl` only, so a `current: {"value": "$__all"}` written into the
#     FILE meets the reset (r4 A4) that a link's `?var-guest=$__all` escapes.
#   * `label` — the picker's caption, read only by `VariableValueSelectors` (D4).
#     A wrong caption is 4d's eye, not a gate's.
#   * `regexApplyTo` — measured unreadable in round 2 (calibration R4).
#
# A KEY OUTSIDE THIS SET IS PRINTED, NOT FAILED. Grafana adds variable fields
# between releases and a dashboard re-saved through a newer one would redden for
# a field that changes nothing — the same false refusal this row pays to avoid
# everywhere else. Printing puts the next key of that class on the gate's own
# output instead of in the next review.
#
# AND THE PRINTER'S OWN BOUND, WHICH ROUND 4's REVIEW IS: it speaks for keys
# OUTSIDE this set and says nothing about a key INSIDE it whose pricing has gone
# stale. That is not a hole a printer can close — it is closed by re-reading each
# entry above against what the rule ACCEPTS every time the rule's shape moves.
GRAFANA_PVE_DROP_DOWN_KEYS_PRICED = frozenset({
    "allValue", "current", "datasource", "definition", "hide", "includeAll", "label", "multi",
    "name", "options", "query", "refresh", "regex", "regexApplyTo", "sort", "type"})

# HOW A DASHBOARD SPELLS A VARIABLE REFERENCE — Grafana 13.1.0's OWN regex,
# copied out of the pinned image rather than transcribed from the docs
# (`logs/calibration-step05a-grafana-interpolation.sh` / `.log`: the webpack
# bundles ship `.js.map` sidecars carrying `sourcesContent`, so the original
# TypeScript is readable byte-for-byte offline. Both
# `public/app/features/variables/utils.ts` and
# `public/app/features/dashboard-scene/variables/utils.ts` declare the IDENTICAL
# literal `/\$(\w+)|\[\[(\w+?)(?::(\w+))?\]\]|\${(\w+)(?:\.([^:^\}]+))?(?::([^\}]+))?}/g`).
#
# WHY THE SHIPPED GRAMMAR AND NOT THE SPELLING THESE FILES HAPPEN TO USE. The
# delivered PVE dashboard writes `$guest` thirteen times and nothing else, so a
# tokeniser that formed only `$name` would look complete and be blind to
# `${guest}` and `[[guest]]` — and a near-miss the pattern cannot FORM is not a
# rejected reference, it is an INVISIBLE one, which is exactly the six-round
# defect DEC-077 closed for metric names. The three alternations are kept in
# Grafana's order, including the `[^:^\}]` character class whose second `^` is
# literal in JS and is literal here too.
#
# ONE THING HAD TO BE TRANSLATED RATHER THAN COPIED, AND `re.ASCII` IS IT.
# JavaScript's `\w` is `[A-Za-z0-9_]`; Python's is Unicode, so it also matches
# `é`, `ß`, `Ω`. Left alone, the two tokenisers disagree on the very case a
# transcription is supposed to get right: a title reading `$guesté` is `$guest`
# followed by a literal `é` to Grafana — the reference RESOLVES and the panel is
# correct — while an unflagged Python `\w+` forms `guesté`, finds no such
# declaration and reddens a dashboard that works. `re.ASCII` narrows `\w` (and
# `\b`, `\s`, `\d`) to the ASCII sense JS uses; no other construct in the pattern
# is affected, and the divergence is a difference in the ALPHABET the two engines
# read, not in the grammar. A false refusal here would be the class this repo has
# already been rejected twice for.
#
# The three capture groups that hold a NAME are 1 (`$name`), 2 (`[[name]]`) and
# 4 (`${name}`); groups 3 and 6 are the format option (`[[guest:csv]]`,
# `${guest:raw}`) and 5 is the dotted tail of a built-in (`${__field.labels.x}`).
# None of those three is a variable name, so none of them is looked up.
_GRAFANA_INTERPOLATION = re.compile(
    r"\$(\w+)|\[\[(\w+?)(?::(\w+))?\]\]|\$\{(\w+)(?:\.([^:^}]+))?(?::([^}]+))?\}",
    re.ASCII)

# THE BUILT-INS ARE A SET, SOURCED — AND THE `__` PREFIX RULE THAT STOOD HERE WAS
# A HOLE. The prefix has an argument, and it is nearly right: Grafana's
# variable-NAME validator is `RESERVED_GLOBAL_VARIABLE_NAME_REGEX = /^(?!__).*$/`
# ("Template names cannot begin with '__', that's reserved for Grafana's global
# variables"), so `__` is exactly the set of names a dashboard may not DECLARE.
# It is NOT the set of names Grafana SUBSTITUTES, and substitution is what this
# row is about. The substituter, out of the same image
# (`public/app/features/templating/template_srv.ts`):
#
#     private _evaluateVariableExpression(match, variableName, fieldPath, …) {
#       const variable = this.getVariableAtIndex(variableName);
#       …
#       if (!variable) {
#         const macro = macroRegistry[variableName];
#         if (macro) { return macro(match, fieldPath, scopedVars, format); }
#         return match;                    // <-- LEFT LITERAL
#       }
#
# A `__` name that is neither declared nor a registered macro stays in the query
# verbatim. Measured on the delivered tree: ONE target's `{id="$guest"}` written
# `{id="$__guest"}` — an ordinary slip — leaves the whole guard PASS while that
# panel draws "No data", and `$__rate_intervall` and `${__feild.displayName}` do
# the same. A reserved prefix says what an author may not declare; the gap
# between that and what the runtime substitutes is the silent class this row
# exists for, one namespace over.
#
# DIRECTION SETTLES THE TRADE. A sourced set that goes stale errs LOUD — a global
# Grafana adds later reddens a real dashboard on the next `just test`, naming it.
# The prefix errs SILENT. So the set is the fail-closed choice even though it is
# the one that needs maintaining.
#
# EVERY NAME BELOW IS READ OUT OF grafana/grafana:13.1.0, NOT RECALLED
# (`logs/calibration-step05a-grafana-builtin-set.py` / `.log`, offline off the
# `.js.map` sourcesContent the `.sh` already extracted). Every extractor there
# RAISES on a miss, because the previous calibration printed "!! macro map not
# matched" and the fallback was read as a design decision instead of an
# instrument failure. Four sources, and the UNION is the point — no one of them
# is complete:
#
#   * `public/app/features/explore/utils/links.ts::builtInVariables`, which is
#     Grafana's own answer to this exact question, kept beside the docs URL that
#     defines them: `__from __to __interval __interval_ms __org __user __range
#     __rate_interval __timeFilter timeFilter`, plus `__dashboard` and `__name`,
#     which that file comments out as "only applicable in dashboards" — which is
#     what every file this guard reads is.
#   * `public/app/features/templating/macroRegistry.ts`, the map
#     `_evaluateVariableExpression` consults above: `__value __data __series
#     __field __timezone`, plus its two COMPUTED keys resolved through
#     `packages/grafana-data/src/utils/dataLinks.ts::DataLinkBuiltInVars`
#     (`__all_variables`, `__url_time_range`).
#   * `@grafana/prometheus/dist/esm/datasource.mjs::getIntervalVars` and
#     `::getRangeScopedVars` — the only datasource this role provisions, adding
#     `__interval __interval_ms __range __range_ms __range_s` at query time.
#     `__range_s` and `__range_ms` appear in no other source here; the plugin's
#     own `tracking.mjs::partsToKeep` census is read as a cross-check that the
#     union leaves nothing over.
#   * `variables/constants.ts::ALL_VARIABLE_VALUE` (`$__all`),
#     `grafana-data/utils/variables.ts::SEARCH_FILTER_VARIABLE`, and the two
#     auto-interval spellings (`interval/actions.ts`'s `$__auto_interval`, and
#     the scenes-era `$__auto` in `transformSaveModelSchemaV2ToScene.ts`).
#
# THE DOTTED SPELLINGS ARE ABSENT AND DO NOT NEED TO BE HERE. `DataLinkBuiltInVars`
# carries eight of them (`__field.displayName`, `__value.calc`, …) and Grafana's
# tokeniser stops a name at the dot — `\w` excludes it, and the `${…}` form puts
# the dotted tail in its own capture group — so what is ever looked up is the
# HEAD. The calibration asserts that every one of those heads is independently
# sourced, so dropping the tails loses nothing.
#
# TWO BOUNDS, STATED RATHER THAN LEFT TO BE FOUND. (1) `$__auto_interval_<name>`
# is registered once per interval variable, so it is a FAMILY and not a name; it
# is deliberately NOT here, because a prefix is the shape this constant replaces,
# no delivered dashboard declares an interval variable, and the refusal would be
# loud. (2) `timeFilter` is exempt because Grafana's own list carries it, even
# though it is an InfluxDB/SQL macro that Prometheus does not substitute — on
# this role's datasources a panel using it would be silently empty, and that is
# 4d's operator eye rather than this row.
GRAFANA_BUILT_IN_VARIABLES = frozenset({
    "__all", "__all_variables", "__auto", "__auto_interval", "__dashboard",
    "__data", "__field", "__from", "__interval", "__interval_ms", "__name",
    "__org", "__range", "__range_ms", "__range_s", "__rate_interval",
    "__searchFilter", "__series", "__timeFilter", "__timezone", "__to",
    "__url_time_range", "__user", "__value", "timeFilter",
})

# GRAFANA IS NOT THE ONLY GRAMMAR THAT OWNS `$` INSIDE A DASHBOARD STRING, and
# the other one spells its references with DIGITS. `\w` includes `0-9` in both
# engines — `re.ASCII` narrows the alphabet, it does not drop the digits — so
# `$1` and `${1}` are variable references to the grammar above. They are
# references to Grafana too, and Grafana's answer is the branch quoted for the
# built-ins: `"1"` is neither a declared variable nor a registered macro, there
# is no digit special-casing anywhere on that path, so `_evaluateVariableExpression`
# returns `match` and `$1` REACHES PROMETHEUS VERBATIM. Which is the whole
# point: `$1` is PromQL's only spelling for a regex capture group in
# `label_replace`, so leaving it literal is what makes the query work.
#
# MEASURED, BOTH HALVES (`logs/calibration-step05a-r3-capture-group.py` / `.log`,
# 7/7, and every extractor there raises on a miss): out of grafana/grafana:13.1.0,
# the `return match` branch and the absence of any digit branch in
# `template_srv.ts`; out of prom/prometheus:v3.12.0 via `promtool test rules`,
# `label_replace(pve_up{id="lxc/110"}, "guest_name", "$1", "id", "lxc/(.*)")`
# yielding `guest_name="110"`, the same expression with a bare `1` yielding the
# literal `guest_name="1"` (so the sigil is load-bearing and there is no
# sigil-free spelling to prefer), and Go's `${1}` yielding `"110"` as well —
# so this constant is the NUMBERED half of Go's grammar. THE NAMED HALF IS THE
# CONSTANT BELOW, and round 3 shipped this one alone while claiming it settled
# "the NAME"; it settles the names that are DIGITS. WHICH TEXTS a digit may be
# written as for this to fire is a third question, and neither this constant nor
# the one below answers it — `_PROMQL_EXPAND_REFERENCE` does, because Grafana can
# spell `1` five ways Go does not read (`[[1]]`, `${1:raw}`, …) and round 4
# skipped all of them.
#
# NOT DISTANT, AND NOT HYPOTHETICAL. The delivered variable is
# `label_values(pve_up{id=~"lxc/.*"}, id)`, so the drop-down lists the raw ids
# `lxc/110` / `lxc/111`, while the Test Requirement this row's docstring opens by
# quoting asks it to list "CT 110 (Plex) and CT 111 (docker-host)". Turning the
# id into a name IS a `$1` `label_replace`. Without this, the guard reddens the
# next edit its own justification asks for, at the 4d operator gate.
#
# WHAT IT COSTS, STATED AS A CLAIM ABOUT ONE SPELLING AND NOT AS A CENSUS. The
# skip applies only when the name is not declared, so a dashboard that really
# declares a variable named `1` (`WORD_CHARACTERS_REGEX = /^\w+$/` permits it)
# is checked normally and D2 proves it. What is given up is therefore exactly
# one thing: a dangling reference to an undeclared ALL-DIGIT name WRITTEN `$1` OR
# `${1}` — the two texts Go reads, since round 5 the other five are refused. No
# reader can tell that one from a capture group — Grafana cannot, since both take
# the same `return match` branch — so the coverage was never really there to
# lose. This
# sentence says nothing about what other grammars may come to share the sigil
# inside a dashboard string; assume that enumeration is incomplete.
_PROMQL_CAPTURE_GROUP = re.compile(r"[0-9]+\Z")

# THE SAME GO GRAMMAR, REFERENCING THE SAME GROUP BY NAME — the half round 3
# missed while asserting it had covered "the NAME". `label_replace` calls Go's
# `Regexp.Expand`, and Expand resolves `$name` and `${name}` against a group
# declared `(?P<name>…)` exactly as it resolves `$1` against the first one. So
# `label_replace(pve_up{id="$guest"}, "guest_name", "$ct", "id", "lxc/(?P<ct>.*)")`
# is a WORKING query in which `$ct` must reach Prometheus untouched — and to the
# Grafana grammar above it is an undeclared variable reference, refused with the
# sentence "Grafana substitutes nothing and the panel queries the literal text",
# which is a description of the mechanism that makes it work.
#
# ENUMERATED FROM THE ENGINE, NOT FROM THE EXAMPLE THAT PROMPTED THE FIX, which
# is what round 3 did with `$1` and is why there was a round 4
# (`logs/calibration-step05a-r4-named-group.py` / `.log`, 10/10, every extractor
# raising on a miss, `prom/prometheus:v3.12.0` via `promtool test rules` and
# `grafana/grafana:13.1.0` off its `.js.map` sourcesContent):
#
#   * `(?P<ct>…)` with `"$ct"` and with `"${ct}"` both draw `guest_name="110"`
#     out of `lxc/110` (B1, B2) — two spellings of the reference.
#   * `(?<ct>…)` — Go 1.22's synonym for `(?P<…>` — is ACCEPTED by this build
#     and draws the same value (B3). Nobody had named this one; a declaration
#     pattern without the `P?` would refuse a query the pinned engine runs.
#   * A group name is `\w`, the alphabet Grafana's tokeniser forms a name out of
#     (B4, `(?P<ct_1>…)` + `$ct_1`), so ONE reader decides both sides.
#   * Grafana hands the reference over intact: the `if (!variable)` branch
#     `return match`s (A1) and nothing on that path knows what a capture group
#     is (A2), so `$ct` and a dangling `$guestt` are one event at the runtime.
#
# WHY THE SKIP IS CONDITIONED ON THE DECLARATION BEING IN THE SAME STRING rather
# than on the name looking group-like: an undeclared name is not inert the way an
# undeclared `$1` is. `"$ct"` against a regex that declares no `ct` expands to
# THE EMPTY STRING (B5) — a silently broken query, which is this row's whole
# subject. So the exemption asks the string what it declares, and where the
# string declares nothing the row still refuses. The same measurement settles
# EXACTNESS: Go takes a name as long as possible, so `$ctx` beside `(?P<ct>…)`
# is `${ctx}` and expands to empty (B6); an exact-name test agrees with the
# engine and a prefix test would wave a dead query through.
#
# THE BOUND, STATED AS A CLAIM ABOUT ONE SCOPE AND NOT AS A CENSUS. Go expands
# against `label_replace`'s regex ARGUMENT only: a `(?P<ct>…)` written in a
# MATCHER beside the call does not resolve in it (B8), yet both sit in one JSON
# string and this test is per-string. So what is given up is a dangling `$name`
# in a string that separately declares a group of that name somewhere Expand
# cannot see — narrower than the alternative (pairing each `label_replace`'s
# replacement to its own regex argument), and the direction is deliberate: a
# per-call reader would have to decide what every OTHER function does with a `$`
# too. Across strings it fails closed. This sentence is about `$`-in-a-Go-regexp
# and nothing else; it is not a census of what may come to share the sigil.
#
# GO'S `$$` LITERAL-`$` ESCAPE — MEASURED SINCE ROUND 3, AND REFUSED RATHER THAN
# WAVED THROUGH SINCE ROUND 6. `"$$ct"` really does produce the text `$ct` (B7),
# so it is not a capture reference at all: the panel draws the literal `$ct`
# where the author meant `110`. Round 5's sentence here said it "is not skipped,
# because it is not usable here for a reason that is Grafana's" — `\$(\w+)`
# cannot match the first `$`, so Grafana reads `$$guestt` as the reference
# `$guestt` and substitutes it before Prometheus sees anything. That reasoning is
# sound and it does not reach the case this row is about: an UNDECLARED name is
# the one Grafana leaves LITERAL (`return match`), so `$$ct` arrives at Go
# untouched, and the tokeniser's match starts at the SECOND `$` where nothing
# looked left. It was skipped. It is the same question as the alphabet boundary
# one paragraph down — does Go read a reference HERE, and does it read THIS name
# — so it is answered in the same predicate, by the parity of the `$` run before
# the match. Both parities and both spellings are measured
# (`logs/calibration-step05a-r6-name-boundary.py`, H1-H5: `$$ct` → `$ct`,
# `$$$ct` → `$110`, `$$$$ct` → `$$ct`, `$${ct}` → `${ct}`, `x$$-$ct` → `x$-110`).
# No delivered dashboard contains a `$$` today — which is why this was invisible,
# not why it was safe.
_PROMQL_GROUP_DECLARATION = re.compile(r"\(\?P?<(\w+)>", re.ASCII)

# WHICH SPELLING — THE THIRD FACT THE SKIP NEEDS, AND THE ONE ROUNDS 3 AND 4 BOTH
# LEFT OUT. The two constants above settle which NAMES Go resolves. They say
# nothing about which TEXTS, and a name is not a text: Grafana forms one name out
# of SEVEN of them — `$ct`, `${ct}`, `${ct:raw}`, `${ct.tail}`, `${ct.tail:raw}`,
# `[[ct]]`, `[[ct:csv]]` — while round 4's predicate was handed the name alone,
# the caller holding the matched text and not passing it. So the skip fired for
# all seven, and the exemption's whole argument ("Grafana passes the reference
# through untouched, which is what makes the query work") is available only for
# the spellings Go then picks up. For the rest the text reaches the TSDB verbatim
# and the panel draws a label that reads `[[ct]]` — the silent breakage this row
# exists for, waved through by the row itself.
#
# THE ACCEPT SIDE IS THEREFORE THE INTERSECTION OF THE TWO GRAMMARS, NOT EITHER
# ONE'S NAMES, and it is enumerated EXHAUSTIVELY rather than from the examples
# that prompted the fix — which is the mistake rounds 3 and 4 were each rejected
# for once (`logs/calibration-step05a-r5-spelling-intersection.py` / `.log`,
# 19/19, every extractor raising on a miss). The exhaustiveness is mechanical
# rather than a claim: that file pins `_GRAFANA_INTERPOLATION` by pattern text AND
# by group count — three alternations, two independent optional suffixes on the
# third, so 1 + 2 + 2*2 = 7 is the whole set a name can be written as, and an
# added alternation invalidates the pin loudly. It then makes THIS FILE'S OWN
# tokeniser read each of the fourteen texts (both halves of Go's grammar) as the
# name under test, so the engine is asked about what the guard actually sees. On
# `prom/prometheus:v3.12.0`, per text:
#
#   * `$ct` and `${ct}` draw `guest_name="110"` out of `lxc/(?P<ct>.*)` (G1, G2);
#     `$1` and `${1}` do the same out of `lxc/(.*)` (N1, N2). Four texts, two
#     spellings, both halves.
#   * THE OTHER FIVE REACH THE TSDB AS TEXT, on both halves and with no exception:
#     `guest_name="${ct:raw}"`, `"${ct.tail}"`, `"${ct.tail:raw}"`, `"[[ct]]"`,
#     `"[[ct:csv]]"` (G3-G7), and `"${1:raw}"`, `"${1.tail}"`, `"${1.tail:raw}"`,
#     `"[[1]]"`, `"[[1:csv]]"` (N3-N7). `${ct.tail:raw}` — tail AND format
#     together — is a text no earlier calibration or review in this objective had
#     put to the engine, which is the argument for enumerating over listing.
#
# WHY THE NAME IS READ BACK OUT OF THE TEXT instead of taken from the caller: it
# makes this a statement about Go rather than a second-hand one. The two texts
# accepted here are the two Go's own `extract()` accepts, and — ONCE THE NAME IS
# MADE TO END WHERE GO ENDS IT — the name Go takes from each is the name Grafana
# took from it, so the caller's declared-wins test governs exactly the token this
# asks about.
#
# THAT CLAUSE IS ROUND 6'S CORRECTION, AND IT IS NOT A REFINEMENT. Round 5 wrote
# here that `re.ASCII` "holds the name alphabet to Grafana's; Go's is
# Unicode-wide, so that is a narrowing of the ACCEPT side and can only refuse,
# never wave through". The premise is right and the conclusion is backwards, for
# a reason that is about the ANCHOR rather than the alphabet: `\Z` binds this
# pattern to the end of THE TEXT GRAFANA MATCHED, and Grafana's match stops at
# the ASCII boundary. So `$ctß` arrives here as the text `$ct`, is accepted, and
# is read as the name `ct` — while Go reads `ctß`, finds no such group, and
# expands it to nothing (measured: the label is dropped outright). The ASCII name
# is a PREFIX of Go's, and a declared prefix exempted an undeclared full name.
# That is the wave-through direction, not the refusal one. What no anchor inside
# the text can see is the character AFTER it; `_go_expand_absorbs` is that half,
# and `_promql_capture_reference` asks both. DEC-107.
_PROMQL_EXPAND_REFERENCE = re.compile(r"\$(?:(\w+)|\{(\w+)\})\Z", re.ASCII)

# THE ONE FIELD IN THE SAVE MODEL THAT NAMES A VARIABLE WITH NO SIGIL, which is
# why the grammar above cannot see it. `transformSaveModelToScene.ts` reads
# `panel.repeat` and `row.repeat` straight into a scene object's `variableName`,
# and the renderer then resolves it by NAME —
# `sceneGraph.lookupVariable(this.state.variableName, …)` in
# `DashboardGridItem.tsx` and `RowRepeaterBehavior.ts`. The v1 schema declares it
# twice, once on Panel and once on RowPanel, as `repeat?: string` — "Name of
# template variable to repeat for" (`types.gen.ts`). A rename that fixes every
# `$guest` and leaves `repeat: guest` behind stops the panel repeating with
# nothing anywhere saying so, which is why the carrier is read rather than
# claimed.
GRAFANA_BARE_VARIABLE_KEY = "repeat"

# AND THE ONE ENTRY WHOSE CHILDREN ARE NOT WHERE THE SAVE MODEL PUTS THEM. A ROW
# owns panels; which panels it owns is decided by `collapsed`, and only ONE of the
# two spellings nests them under the row. Round 4 read containment as a json-path
# prefix and stated its width as "a repeating ROW covers the panels nested in it",
# which is the COLLAPSED spelling — and the EXPANDED one is the row-repeat UI's
# default and the one Grafana writes. Measured out of grafana/grafana:13.1.0's own
# sourcesContent (the review's `logs/critic-step05d-r4-rowrepeat-calib.py`, 12/12,
# offline, nothing started; re-run verbatim as `-r5recheck`):
#
#   * `createSceneObjectsForPanels` makes a row `currentRow` only when
#     `Boolean(panel.collapsed)` is FALSE, then pushes every FOLLOWING top-level
#     panel into `currentRowPanels` and commits them with
#     `createRowFromPanelModel(currentRow, currentRowPanels)` at the NEXT row and
#     at the end of the list (A1-A3). A collapsed row takes the other branch,
#     under Grafana's own comment "collapsed rows contain their panels within the
#     row model" (A4) — so its SIBLINGS stay at top level and are nobody's
#     children.
#   * `createRowFromPanelModel` attaches `new RowRepeaterBehavior({variableName:
#     row.repeat})` on `if (row.repeat)` ALONE (B1). `collapsed` decides where the
#     children came from and nothing else.
#   * `performRepeat` then calls the SAME `getMultiVariableValues` and
#     `getLocalVariableValueSet` the panel exemption rests on, over `rowContent =
#     rowToRepeat.state.children` — i.e. exactly the siblings A2 collected — and
#     gives every clone, `rowIndex === 0` included, ONE bare id (C1-C5).
#   * `gridRowToSaveModel` writes `panels: []` on EVERY row and `repeat` beside it
#     (D1/D2), so a row the operator never collapsed saves as an entry whose
#     children are its siblings.
#
# `collapsed` is read with JS truthiness on the JSON scalar (`Boolean(…)` above),
# which is `GRAFANA_FALSY_VALUES` — `"false"` is a TRUE flag here as everywhere
# else in this file, and `0` is not one.
GRAFANA_ROW_PANEL_TYPE = "row"
GRAFANA_ROW_COLLAPSED_KEY = "collapsed"

# AND "FOLLOWING" IS A POSITION ON THE SCREEN, NOT AN INDEX IN THE FILE. The list
# `createSceneObjectsForPanels` walks is not the list the JSON holds: Grafana sorts
# it first, so for any dashboard whose array order is not its `gridPos` order the
# row's children and the entries after it in the file are DIFFERENT SETS. Measured
# out of the same pinned grafana/grafana:13.1.0 — the review's
# `logs/critic-step05d-r5-gridpos.py` A1-A6 (re-run verbatim as `-r6recheck`) and
# this round's `logs/calibration-step05d-rework-r6-gridpos.py`:
#
#   * `DashboardModel`'s CONSTRUCTOR calls `sortPanelsByGridPos()`, whose comparator
#     is `panelA.gridPos.y === panelB.gridPos.y ? .x - .x : .y - .y` (A1/A2), and
#     `transformSaveModelToScene` builds that very model — "just to have migrations
#     run", but the sort runs too — before handing `createSceneObjectsForPanels
#     (oldModel.panels)` the SORTED array (A3/A4). The row-collection loop is
#     `for (const panel of oldPanels)` (A5) and `DashboardModel.getRowPanels` slices
#     the same sorted list (A6).
#   * SO A HAND-AUTHORED FILE — the only kind this repo has, since Grafana saves
#     from its own already-sorted `this.panels` — can put a row anywhere in the
#     array and anywhere on the screen independently, and the two harms are
#     opposite: a row written first at `y: 999` repeats NOTHING while an array
#     reading exempts every panel after it, and a row appended last at `y: -1`
#     repeats everything while an array reading refuses it.
#
# THE DEFAULT IS MEASURED, NOT ASSUMED. Every `panels[]` entry — rows included —
# becomes a `PanelModel` before the sort (`this.panels = map(data.panels ?? [],
# (p) => new PanelModel(p))`, P1/P2/P5), and `PanelModel` applies
# `defaultsDeep(this, cloneDeep({gridPos: {x: 0, y: 0, h: 3, w: 6}, …}))` (P3/P4).
# DEEP: a partial `{"x": 0}` reaches the comparator with `y` filled to 0, so an
# unpositioned entry sorts at the origin rather than nowhere.
#
# AND A POSITION IS A JSON NUMBER, WHICH IS NOT THE SAME QUESTION AS "CAN GRAFANA
# SUBTRACT IT". The comparator is TWO operators and they disagree, so the rule has to
# be read off both — `logs/calibration-step05d-rework-r7-axis.py`, node itself and the
# image's own lodash:
#
#   a.gridPos.y === b.gridPos.y ? a.gridPos.x - b.gridPos.x : a.gridPos.y - b.gridPos.y
#
#   * `===` decides whether the `x` tie-break happens at all, and `-` decides the
#     order otherwise. `true`, `false`, `null`, `""` and `[]` all SUBTRACT to a
#     number and are none of them `===` to it (C2), so against that very number the
#     comparator answers 0 — "equal", with the tie-break skipped — while against any
#     OTHER number it orders normally, and against a second entry carrying the same
#     spelling it ties on `x` after all (C3). Ordered like `n` and never tied with
#     `n` is not a place: the same entry is equal to and ordered against the same
#     panel depending on which pairs the sort happened to compare. `"3"` and `[3]`
#     are the same class one step out (C4/C5); `"top"` and `{}` reach the comparator
#     as NaN, which SortCompare turns into +0 — "equal to everything".
#   * SO NEITHER HALF CAN BE READ AS ITS NUMBER. A `null` axis orders exactly like
#     the origin in a list with no numeric 0 in it (T4) and NOT in a list that has
#     one (T1) — both measured, both true — so a reader that sees one value at a time
#     cannot say which list it is in. `_grafana_row_span` withholds the span for the
#     whole class instead: a refusal, loud and one character to undo, in the
#     direction this file pays everywhere else.
#   * THE `x` AXIS IS GENUINELY MORE PERMISSIVE, and this is refused anyway. Its
#     branch is a bare subtraction with no `===` in front of it, so `x: true` really
#     does read as 1 and that dashboard really does work (r7 B4, a scored false
#     refusal). Accepting it means implementing JS `ToNumber` — over strings, arrays
#     and the empty string — which is a bigger claim than the one it would buy, and
#     it widens the ACCEPT side, which is the side this row exists to hold.
#   * AND THE NUMBER IS A DOUBLE. Python's `json` keeps `9007199254740993` and
#     `9007199254740992` apart as exact ints; `JSON.parse` collapses them onto one
#     double, so Grafana TIES and lets `x` decide where an int key orders by `y`
#     (N1/N2). Every axis is therefore read as `float`.
#   * AND THE VALUES THAT ARE NOT DOUBLES AT ALL ARE NOT THIS FUNCTION'S QUESTION.
#     Round 7 answered them here — a bare `NaN` token withheld, an `Infinity` token
#     read as a place, an int past the double range converted into "the infinity
#     `JSON.parse` gives it" — which split three spellings the delivery path treats
#     identically, and answered only for the one field this reader happens to look at.
#     A delivered file meets Go's `encoding/json` first and Go refuses ALL of them, on
#     an axis or in a `fieldConfig` nothing reads (`logs/critic-step05d-r7-nonfinite-
#     token.py` B2/B3/B5, `logs/calibration-step05d-rework-r8-number-range.py` B2/B6).
#     So the whole class is refused at the parse, by `_grafana_provisionable_json`,
#     which is where the engine refuses it — and the small end of the range, which the
#     engine ACCEPTS, is accepted here (calibration B5).
#
# AND `gridPos` ABSENT IS NOT `gridPos` WRITTEN AS null. They are one thing to
# `dict.get` and two things to the engine: `defaultsDeep` replaces only what is
# `undefined`, so the absent key is filled to the origin (L3) while a written `null`
# survives — and the comparator reading `.y` off null THROWS, taking the whole
# dashboard with it (L6). A primitive `gridPos` survives too and reads `.y` as
# undefined, i.e. NaN (L7); an ARRAY is a third answer again, because lodash's
# `isObject` is true of one and the axes are merged onto it as named properties, so it
# reads as the origin (L8) — and it is refused with the rest, for B4's reason. Only
# the absent key is a position here, so the membership test is `in` and never `.get`.
GRAFANA_PANEL_POSITION_KEY = "gridPos"
GRAFANA_PANEL_POSITION_AXES = ("y", "x")
GRAFANA_PANEL_POSITION_DEFAULT = 0
# The ONE list that sort is applied to. `createRowFromPanelModel` reads a COLLAPSED
# row's children with a plain `row.panels.map(…)` — no sort — so a nested list keeps
# its file order, and this is the json path of the dashboard's own `panels[]`.
GRAFANA_SORTED_PANEL_LIST_PATH = "$"

# Every `pve_*` series the PINNED exporter can emit, READ OUT OF THE IMAGE by
# AST rather than from the README or from memory
# (`logs/calibration-step04b-pve-series.py` / `.log`, image
# `prompve/prometheus-pve-exporter:3.9.0` = the tag `defaults/main.yml` pins,
# digest sha256:78a58df7…0757f; 38 families across `collector/cluster.py` and
# `collector/node.py`, counting both the direct `GaugeMetricFamily('pve_x', …)`
# spelling and the `super().__init__('pve_x', …)` one that `pve_ha_state` and
# `pve_lock_state` use).
#
# WHY AN ALLOW-LIST AND NOT A PATTERN. Step 4b's task says the metric names are
# not the Builder's to invent, and a dashboard whose panels are all "No data"
# because a name is a near-miss (`pve_memory_used_bytes` for the real
# `pve_memory_usage_bytes`) is exactly the silent failure 4d's operator would
# have to catch by eye. A `pve_.*` pattern accepts every typo; this does not.
#
# WHAT IT DOES NOT CLAIM. That the live PVE API returns the key that populates a
# given family, for THIS cluster, for a container. `ClusterResourcesCollector`
# emits a sample only when the API response carries the matching key, and the
# exporter's own docstrings say the block-I/O families are "not available for all
# storage types". Existence-in-the-vocabulary is offline-checkable; existence-in-
# the-TSDB is 4d's, and the delivery task in tasks/main.yml names which panels
# rest on which half.
PVE_EXPORTER_SERIES = frozenset({
    "pve_cluster_info", "pve_cpu_usage_limit", "pve_cpu_usage_ratio",
    "pve_disk_read_bytes", "pve_disk_read_bytes_total", "pve_disk_size_bytes",
    "pve_disk_usage_bytes", "pve_disk_write_bytes", "pve_disk_written_bytes_total",
    "pve_guest_info", "pve_ha_state", "pve_lock_state", "pve_memory_size_bytes",
    "pve_memory_usage_bytes", "pve_network_receive_bytes",
    "pve_network_receive_bytes_total", "pve_network_transmit_bytes",
    "pve_network_transmit_bytes_total", "pve_node_info", "pve_not_backed_up_info",
    "pve_not_backed_up_total", "pve_onboot_status", "pve_qdevice_info",
    "pve_qdevice_up", "pve_replication_duration_seconds",
    "pve_replication_failed_syncs", "pve_replication_info",
    "pve_replication_last_sync_timestamp_seconds",
    "pve_replication_last_try_timestamp_seconds",
    "pve_replication_next_sync_timestamp_seconds", "pve_storage_info",
    "pve_storage_shared", "pve_subscription_info",
    "pve_subscription_next_due_timestamp_seconds", "pve_subscription_status",
    "pve_up", "pve_uptime_seconds", "pve_version_info",
})

# THE PROXMOX DASHBOARD'S IDENTITY, AND IT IS THE DASHBOARD'S OWN `uid` RATHER
# THAN THE FILE IT SHIPS AS. The row below is the one check in this file that
# speaks about ONE delivered dashboard instead of the inventory, so it has to say
# which one, and the answer is not free of consequence — an identity pin that
# silently matches nothing is the same vacuity failure the row exists to close,
# one level up (the task says so in those words, and DEC-133 records the choice).
#
# THREE SPELLINGS WERE AVAILABLE and only one is the dashboard's own name for
# itself. The `src:` (`grafana-pve-dashboard.json`) and the `dest:` (`pve.json`)
# are ANSIBLE's names: renaming either changes nothing an operator sees, and
# `test_delivered_dashboards_have_distinct_uids`' measurement U2 is the proof
# that the file name is not identity — which of two uid-colliding dashboards
# SURVIVED flipped when only the file names changed. The `uid` is what Grafana
# keys the store by, what the provider warns about when two collide, and what
# `tasks/main.yml` already documents as a contract ("The dashboard `uid` is
# `pve-overview` and it MUST stay distinct from the starter's
# `homelab-overview`"). So the pin is on the identity Grafana itself uses, and
# the two ansible-side names stay free to change.
#
# WHAT HAPPENS WHEN IT MATCHES NOTHING: the row FAILS, naming the uid it looked
# for and listing what the inventory did hold. Both routes to that state are
# real and neither is silent-safe — the delivery task deleted (the dashboard is
# gone, and with it Step 4's Test Requirement) or the `uid` edited (the pin has
# gone stale, and the fix is this one line). The alternative, treating "no such
# dashboard" as "nothing to check", is the exact shape of the hole this row
# closes: a number printed over an empty population.
PVE_DASHBOARD_UID = "pve-overview"

# The label whose VALUES ARE THE GUESTS, and the one series this repo has PINNED
# to this cluster: `pve_up{id="lxc/110"}` is gate 2b's acceptance
# (task-1785324247-3934), and `tasks/main.yml` records that the drop-down is
# deliberately built from it. The drop-down's own query yields values of this
# label and every per-container panel matches them back against it, so the two
# halves of the Test Requirement are one label apart — a drop-down over any other
# label hands the panels strings no series carries.
PVE_GUEST_LABEL = "id"

# THE TEST REQUIREMENT, TRANSCRIBED. Step 4: "verify that the Proxmox dashboard's
# container drop-down correctly lists CT 110 (Plex) and CT 111 (docker-host)".
# Spelled as the exporter spells them — `id="lxc/110"` — because that is the
# form the drop-down's values arrive in and the form the panels match.
#
# THEY ARE PROBES, NOT AN EXPECTED VALUE SET. Nothing offline can know which
# containers the live cluster reports; what is checkable is whether the query the
# dashboard ships ADMITS these two, which is a property of the selector's text
# and is exactly what the mutations that delete the drop-down change.
PVE_TEST_REQUIREMENT_GUESTS = ("lxc/110", "lxc/111")
# What Grafana substitutes for the drop-down when MORE THAN ONE of its values is
# selected — `"(" + escapedValues.join("|") + ")"`, with `/` left alone by
# `prometheusSpecialRegexEscape` so the ids survive as themselves
# (`logs/calibration-step05d-rework-r3-includeall.py` A7/A12). It is built from
# the probes above rather than hardcoded because it is only reachable at all on a
# drop-down this row has already asserted yields both of them, and it appears in
# one message: the reason a literal matcher reading a multi-select variable is
# empty under `=` (engine C1) and unscoped under `!=` (engine C3).
PVE_ALL_ALTERNATION = "(" + "|".join(PVE_TEST_REQUIREMENT_GUESTS) + ")"

# And the other direction, which is what makes "container drop-down" mean
# anything: ids the exporter reports that are NOT containers. `pve_up` carries a
# series per node, per QEMU guest and per storage, all under the same `id` label
# (`logs/calibration-step04b-pve-series.py`), so a selector that has lost its
# `lxc/` scope still admits CT 110 and CT 111 — it just lists the whole cluster
# beside them, under a drop-down labelled Container. A row that probed only the
# ADMIT direction would be satisfied by a selector that pins nothing at all.
PVE_NON_CONTAINER_IDS = ("node/pve", "qemu/110", "storage/local")

# Grafana's own variable-query function — not PromQL, which is why no reader in
# this file formed it until now: the Prometheus datasource resolves
# `label_values(<selector>, <label>)` (and the one-argument
# `label_values(<label>)`) into a `/api/v1/series` call and hands the values to
# the drop-down. It is what the delivered dashboard uses, and reading it is the
# only way to say what the drop-down will CONTAIN rather than merely that it
# exists.
GRAFANA_LABEL_VALUES = "label_values"

# Every `plex_*` series the PINNED exporter can emit, read out of the image the
# same way and for the same reason (`logs/calibration-step04c-plex-series.py` /
# `.log`, `ghcr.io/axsuul/plex-media-server-exporter:2.1.0` = the tag
# `defaults/main.yml:33` pins, digest sha256:ab89d0ba…2cd1; 5/5).
#
# THE NAME IS NOT A LITERAL IN THAT SOURCE, which is the one way this list is
# unlike its `pve_*` sibling and the reason the calibration has a runtime half.
# `collector.rb` registers each family as an INTERPOLATED symbol,
# `@registry.gauge(:"#{@metrics_prefix}_up", …)`, so what is readable off the
# image is the SUFFIX set (7 of them, and all 7 `@registry.<type>(` calls in the
# file were read — row P2, so none is missed) plus the prefix DEFAULT,
# `ENV["METRICS_PREFIX"] || "plex"`. The prefix is not left to that default:
# `compose.yml.j2` writes `METRICS_PREFIX=plex` and
# `scripts/test_traefik_config_shape.py`'s `PLEX_EXPORTER_ENV` already pins that
# key to that value — so THIS list is only correct while that sibling check
# holds, and the calibration's row P4 boots the real exporter at the pinned
# prefix and scrapes `plex_up` off it rather than composing the two files on
# paper.
#
# WHAT IT DOES NOT CLAIM, and here the gap is wider than the PVE one: that any
# of these carries a sample. The exporter emits a family only once a scrape has
# set a value on it, and every collection but the heartbeat is token-gated —
# `PLEX_TOKEN` is empty until Step 3b, an operator gate that has never run. Row
# P4 measured exactly that: with no Plex reachable the running exporter emits
# `plex_up` and NOTHING else. Existence-in-the-vocabulary is offline-checkable;
# existence-in-the-TSDB is 3b's and 4d's.
PLEX_EXPORTER_SERIES = frozenset({
    "plex_audio_transcode_sessions_count", "plex_info", "plex_media_count",
    "plex_media_downloads_count", "plex_sessions_count", "plex_up",
    "plex_video_transcode_sessions_count",
})

# The `service` label VALUE Traefik gives the Plex service, and the histogram
# family whose `le` series Step 1a's bucket ladder tunes. Both MEASURED off
# traefik:v3.7.5 — the tag `defaults/main.yml:11` pins — booted offline with this
# repo's own metrics block and a file-provider `plex` router in front of a whoami
# backend (`logs/calibration-step04c-traefik-plex-series.py` / `.log`, 7/7,
# digest sha256:e4d98158…07c9). Neither was guessable from the config:
#
#   R3  the file-provider service labels as `plex@file`
#   R4  a docker-provider CONTROL on the same proxy labels as `whoami@docker`,
#       so the `@file` half is the PROVIDER and not decoration
#   R5  the 13 boundaries traefik.yml.j2 pins are exactly the `le` values that
#       came back on the plex bucket series, so this family IS what Step 1a tuned
#   R7  `plex@file` never appears on `traefik_entrypoint_request_duration_seconds`
#       — the entrypoint family carries no `service` label at all, which is why
#       the check below bounds itself to the `traefik_service_*` families
TRAEFIK_PLEX_SERVICE = "plex@file"
TRAEFIK_SERVICE_LABEL = "service"
TRAEFIK_SERVICE_LATENCY_BUCKET = "traefik_service_request_duration_seconds_bucket"

# HOW A PromQL CALL TREATS THE LABELS IT IS HANDED. The histogram check below
# rests on this classification, so it is READ OFF THE REAL PARSER rather than off
# the documentation: a grouping modifier is legal ONLY on an aggregation
# operator, so `X by (le) (…)` parses if and only if `X` is one. Every name in
# the first set was confirmed to parse that way and every name in the second was
# confirmed NOT to, in `prom/prometheus:v3.12.0` — the tag `defaults/main.yml:19`
# pins (`logs/calibration-step04c-r2-promql-aggregation.py` / `.log`, 12/12, rows
# A1/A2). The parametrised four (`topk`, `bottomk`, `quantile`, `count_values`)
# are aggregations exactly like the rest; a one-argument probe files them as
# functions, which is how run 1 of that calibration got it wrong.
#
# THE LIST IS NOT CLAIMED TO BE COMPLETE, AND DOES NOT HAVE TO BE. The candidate
# universe of PromQL heads is open — row A4 names two more aggregations that
# Prometheus 3.x ships behind `--enable-feature=promql-experimental-functions`
# and would admit tomorrow. So the check is written as an ALLOW-LIST whose
# unknown case is RED: a head nobody classified makes `just test` refuse loudly
# and costs one line here, instead of passing silently over a panel whose
# quantile has no boundaries. That direction is the whole lesson of
# `mem-1785498725-78ea` — enumerate what is applied, not what happens to be
# written — and of DEC-077 one layer down.
#
# THE NAMES HERE ARE MATCHED CASE-INSENSITIVELY AND THE ONES BELOW THEM ARE NOT,
# and that asymmetry is the parser's, not a convenience. Measured in the same
# image (`logs/calibration-step04c-r3-promql-case.log`, 19/19): an AGGREGATION
# OPERATOR is a keyword and folds — `SUM by (le) (foo)` comes back out of
# `promql format` as `sum by (le) (foo)`, and so does every other name in this
# set including the parametrised four (A1) — while a FUNCTION name does NOT:
# `RATE(foo[5m])` is refused with `unknown function with name "RATE"` (A3').
# So a blanket lower-case would file `RATE(…)` as the label-transparent `rate`
# when the real engine refuses the whole expression, trading one fail-open for
# another. Fold what the parser folds and nothing else.
PROMQL_AGGREGATION_OPERATORS = frozenset({
    "sum", "min", "max", "avg", "group", "stddev", "stdvar",
    "count", "count_values", "bottomk", "topk", "quantile",
})
# THE TWO AGGREGATION OPERATORS THAT DO NOT MERGE ANYTHING. Membership in the set
# above answers the PARSER's question — "does a grouping modifier parse here" —
# which is exactly what round 2's calibration probed, and both checks below then
# read it as "this call collapses the labels I care about". For `topk`/`bottomk`
# that reading is false: they SELECT series, they do not combine them. Measured
# in the same image (`logs/calibration-step04c-r4-promql-quotes-and-selection.log`
# C1-C4): `topk(3, plex_media_count)` returns the three input series with their
# labels — `__name__` included, which a real aggregation drops — `bottomk(2, …)`
# likewise, `topk by (type) (1, …)` hands back the picked series' FULL labels,
# and `histogram_quantile(0.90, topk(3, sum by (le) (rate(…))))` interpolates,
# i.e. `le` survives. Without this split a top-N libraries panel is refused with
# a message about merging that is factually false — the same "guard forbids the
# real answer" failure round 3 was sent to fix one level down.
#
# WHAT A SELECTION DOES INSTEAD IS DROP, and that is why this constant names a
# BEHAVIOUR and leaves the price to each caller. `topk(1, plex_media_count)`
# shows one library (C6) — the panel's stated question — while the same operator
# in front of a histogram removes boundaries from the ladder and the quantile
# goes on drawing: p20 0.3 against a true 0.06 (C9/C9'), and a NaN sample when
# `+Inf` is the one dropped (C8/C8'). So the library row accepts a selection and
# the histogram row refuses it with that measurement in the message. One
# classification, two prices, because the subjects differ — not two answers to
# one question, which is what round 3's DEC-085 forbade.
#
# What selection does NOT do is launder a merge underneath it: in
# `topk(3, sum(plex_media_count))` the `sum` is still classified and still red
# (battery R16).
#
# CASE-INSENSITIVE, like the set above and unlike the one below, because these
# are operators and operators fold (round-3 calibration A1). `limitk`/
# `limit_ratio` — the feature-gated pair that would belong here — are deliberately
# absent: they do not parse in this image (round-3 A6), so nothing has been
# measured about them, and an unclassified head is RED and costs one line.
PROMQL_SERIES_SELECTING_OPERATORS = frozenset({"topk", "bottomk"})
# Calls that hand every label through untouched, so an `le` that entered
# survives. CASE-SENSITIVE, per A3' above.
PROMQL_LABEL_TRANSPARENT_CALLS = frozenset({"rate", "irate", "increase"})
# The one call that CONSUMES `le`, which is its entire job — and therefore the
# call that ENDS the histogram check's interest in what is stacked above it.
PROMQL_HISTOGRAM_QUANTILE = "histogram_quantile"

PROMQL_HEAD_AGGREGATION = "aggregation"
PROMQL_HEAD_TRANSPARENT = "label-transparent"
PROMQL_HEAD_SELECTING = "series-selecting"
PROMQL_HEAD_QUANTILE = "quantile"

# `plex_media_count` carries `labels: [:title, :type]` and `collect_media_metrics`
# emits, per library section, `{title=<library>, type=<library type>}` = that
# section's item count — and then, `when "show"`, a SECOND, SYNTHETIC series
# `{title="<library> - Episodes", type="show_episode"}` = that library's episode
# count. Read out of `/srv/lib/middleware/collector.rb` in the pinned
# `ghcr.io/axsuul/plex-media-server-exporter:2.1.0` (lines 31-35 and 182-214).
# So a bare `sum()` over the family adds every TV library's episodes to its
# titles — see the check below for why that needs a guard rather than an eye.
PLEX_MEDIA_COUNT = "plex_media_count"
PLEX_MEDIA_TYPE_LABEL = "type"
PLEX_MEDIA_SYNTHETIC_TYPE = "show_episode"
# THE SYNTHETIC ROW DIFFERS FROM A REAL LIBRARY ROW IN BOTH OF THE FAMILY'S TWO
# LABELS — it is written `{ title: "#{media_title} - Episodes", type:
# "show_episode" }` — so an aggregation that KEEPS EITHER ONE leaves it a series
# of its own instead of an invisible addend, which is the EFFECT the check below
# is about. Measured, both spellings, in the real engine
# (`logs/calibration-step04c-r3-promql-case.log` B8/B9/B10): `by (title)`,
# `by (type)` and `without (type)` all return the three sections as three
# separate series over a 7-title movie section, a 3-title show section and the
# exporter's 50-episode synthetic row; only a grouping that keeps NEITHER label
# returns the single wrong 60 (B11). Writing the rule over `type` alone — as
# round 2 did — refuses `by (title)`, which is a correct expression, and the
# reason it refuses is that the rule was written per-LABEL while its own
# justification is per-EFFECT.
PLEX_MEDIA_DISTINGUISHING_LABELS = frozenset({"title", "type"})
# The matcher that drops the synthetic rows at the selector. It is ONE spelling of
# the rule and not the rule itself — see `_plex_media_mixed_selector`, which asks
# whether the rows entering a call can be of both KINDS. Kept because it is the
# shape the delivered panel uses and the one the refusal message recommends.
PLEX_MEDIA_EXCLUDED = f'{PLEX_MEDIA_TYPE_LABEL}!="{PLEX_MEDIA_SYNTHETIC_TYPE}"'

# The compose service, its mounts, and the host dir the role delivers into. The
# service name is the anchor for the identity companion check.
#
# PROJECT_DIR is written in the COLLAPSED spelling `{{docker_host_project_dir}}`
# because every path read out of the files goes through `_norm_path()` first —
# the render tasks quote their `dest` and compose does not, and either side may
# space a Jinja expression differently. Spelling the constant the way the
# templates happen to spell it today would make these checks pass or fail on
# whitespace.
GRAFANA_SERVICE = "grafana"
DASHBOARDS_MOUNT = "/var/lib/grafana/dashboards"
PROJECT_DIR = "{{docker_host_project_dir}}"
DASHBOARDS_DIR = f"{PROJECT_DIR}/grafana/dashboards"

# Every grafana path the role must create. Named here rather than derived from
# the file, so DELETING a directory declaration reddens instead of shrinking the
# set the mode check iterates — the vacuity an inventory-only check would have.
REQUIRED_GRAFANA_DIRS = (
    "grafana/provisioning/datasources",
    "grafana/provisioning/dashboards",
    "grafana/dashboards",
)


def _read(path: pathlib.Path) -> str | None:
    """The file's text decoded AS UTF-8, or None when it cannot be read as text.

    BOTH HALVES OF THIS SIGNATURE ARE MEASURED, AND EACH USED TO FAIL A DIFFERENT
    WAY (task-1785571102-579d, routed out of the Step 5d r11 review):

      * `read_text()` raises `UnicodeDecodeError` on a raw invalid byte, and that
        is a ValueError — `except OSError` never caught it, so ONE bad byte in ONE
        delivered dashboard propagated out of `main()` and the gate printed a
        traceback instead of its summary line: rc=1, no `PASS: n/n`, and every
        OTHER row's verdict went with it. The engine does not agree the file is
        broken: `logs/critic-step05d-r11-rawbytes.py` provisioned four such files
        on the pinned grafana/grafana:13.1.0 and 4/4 were SAVED with each bad byte
        replaced by U+FFFD (its B1/B2 discriminate, so "saved" is a measurement).
      * `encoding=` was absent, so the decode used the LOCALE's codec. Under
        `LC_ALL=en_US.iso88591` that same 0xff does not raise at all — it decodes
        to `ÿ`, and the row goes GREEN on a title the engine never stores
        (`logs/red-579d-read-invalid-utf8.py` PART C: 4/4 `PASS: 21/21` before
        this pin). A crash is illegible; that one is a FALSE ACCEPT, and it is why
        the encoding is named here rather than left to the environment.

    Both are the class r10/r11 repaired one layer up at the `\\uD800` escape —
    "the string Python decoded is not the string Go decoded" — at the one site
    where the file's own BYTES decide it.

    The bad bytes are REPORTED, never substituted. Decoding with
    `errors="replace"` would match what Grafana stores and is the loader-wide
    change DEC-150 declined for the escape: it would hand every other row a title
    that is not on disk, and saying so is this guard's job. `_unreadable` turns
    the None back into the sentence for the rows that print a reason.
    """
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _json_string_open_at(raw: bytes, offset: int) -> bool:
    """Whether byte `offset` of `raw` is a CHARACTER position inside a JSON string.

    THE POSITION OF A BAD BYTE DECIDES WHAT THE ENGINE DOES WITH THE FILE, so a
    sentence that names the engine's behaviour has to know which position the
    byte fell in. Go's `encoding/json` substitutes U+FFFD for invalid UTF-8 only
    where it is reading a RUNE; anywhere else an invalid byte is an ordinary
    syntax error and the provisioner never loads the file at all.

    "A STRING IS OPEN" IS NOT THAT RULE, AND THE DIFFERENCE IS TWO MEASURED
    POSITIONS. An open string was this predicate's first spelling and it was
    SUFFICIENT for the substitution — it is not. Measured on the pinned
    `grafana/grafana:13.1.0`, one delivered file per position in ONE provisioning
    run, read back over the HTTP API with the anti-vacuity pair in that same run
    (`logs/red-579d-r3-escape-slot-and-subject.py` PART A/B, and the round-2
    review's `logs/critic-579d-r2-scope-and-escape.py` before it), `0xb0` in the
    `title` string is SAVED as `'H<FFFD>me overview'`, while the SAME byte in the
    two ESCAPE slots of that same string is REFUSED:

        "H<b0>me"        a rune position          -> SAVED
        "H\\<b0>me"       the byte AFTER a `\\`     -> REFUSED
        "H\\u00<b0>me"    a HEX DIGIT of `\\uXXXX`  -> REFUSED

    Both refused positions are INSIDE a string. Go is not reading a character
    there: after `\\` it wants one of `"\\/bfnrtu` and after `\\u` it wants four hex
    digits, so anything else is `invalid character ... in string escape code` —
    a syntax error, and the file is refused exactly as it is outside a string.
    Hence the two extra terms in the return: `escaped` was already computed and
    thrown away, and `uhex` is the four-byte countdown that follows a `\\u`.

    BOTH TERMS ARE OFF-BY-ONE HAZARDS AND BOTH BOUNDARIES ARE MEASURED, in a
    second run of the same engine (`logs/red-579d-r3-countdown-edges.py`, 16/16,
    its own control pair discriminating): the byte AFTER a complete `\\u0041` is a
    character position again and IS SAVED (`'HA<FFFD>me overview'`), the FIRST of
    the four hex digits is REFUSED, and the byte after an escaped `\\\\` or an
    escaped `"` is SAVED — the escape is consumed and the string is still open.
    So the countdown neither starts late nor runs long, and `escaped` clears on
    the byte it consumes.

    Reading the prefix as BYTES is safe and is what makes this cheap: `offset` is
    a `UnicodeDecodeError.start`, so everything before it decoded, and a
    continuation byte of a multi-byte character is `>= 0x80` and can therefore be
    none of `"` (0x22), `\\` (0x5c) or `u` (0x75). JSON has no comments, so an open
    string is the only context a quote can be inside.

    The escape rule is the one JSON has and not a quote count: `\\"` does not
    close a string and `\\\\"` does (`red-579d-r2-position-and-discovery.py`
    A-esc-quote/A-esc-slash pin both directions, and the round-2 review's PART F
    pins that a Jinja literal's quotes come in PAIRS and therefore cancel).
    """
    in_string = escaped = False
    uhex = 0
    for byte in raw[:offset]:
        if uhex:
            uhex -= 1
        elif escaped:
            escaped = False
            if byte == 0x75:               # `u` — four hex digits follow it
                uhex = 4
        elif in_string and byte == 0x5C:
            escaped = True
        elif byte == 0x22:
            in_string = not in_string
    return in_string and not escaped and not uhex


def _unreadable(path: pathlib.Path, *, provisioned: bool = False,
                rendered: bool = False) -> str:
    """Why `_read` returned None — with the byte OFFSET when the bytes decide it.

    Kept out of `_read` so the reading rows keep the `str | None` they already
    test and only the reporting rows pay for the second read. `missing` is the
    word those rows have always printed and it is unchanged for a file that is
    genuinely absent or unopenable — a decode failure is the new sentence, so the
    two cannot be confused (`red-579d-read-invalid-utf8.py` E1/E2).

    THE ENGINE CLAUSE IS TWO-SIDED BECAUSE THE ENGINE IS. One sentence for every
    offset was this row's first spelling and it was wrong for half the positions:
    measured on the pinned `grafana/grafana:13.1.0`, one delivered file per
    position in ONE provisioning run, read back over the HTTP API
    (`logs/critic-579d-bad-byte-position.py` PART A, whose B1/B2 discriminate in
    the same run), `0xff` INSIDE the `title` string is SAVED as
    `'Home<FFFD>lab Overview'` and inside a KEY's string is SAVED with the key
    mangled, while the SAME byte in the structural whitespace and immediately
    after a value are BOTH REFUSED — `failed to load dashboard from`, and absent
    from the API. A reason that is the opposite of the truth costs more than no
    reason: it sends the operator to the Grafana UI to compare a served dashboard
    that does not exist, when the repair is in the container log. So the offset is
    classified rather than assumed, and each branch prints what was measured for
    it. `_json_string_open_at` is that classifier, and the ESCAPE slots it now
    excludes are two more REFUSED positions the first spelling called SAVED.

    AND THE CLAUSE IS EARNED BY THE CALLER, NOT BY THE BYTE. Naming an engine is
    a claim about what READS these bytes, and only a caller that knows the file is
    a delivered dashboard has that: `provisioned=` is passed at six of the seven
    `_unreadable(...)` call sites, and by nothing else. THE UNIT IS THE CALL SITE
    AND NOT THE ROW, which is where an earlier spelling of this sentence went wrong:
    it said FIVE, a count taken over ROWS and worn as a count over CALLERS. Five of
    the six are test rows and the sixth is the HELPER
    `_delivered_dashboard_documents`, which is not a row. The relative clause is not
    what narrows either — fifteen functions call `_delivered_dashboards()` and only
    seven of them reach here. Nor does the helper end the radius: it folds this
    sentence into the `problems` list that seven further rows print — twelve rows
    can carry the clause where five pass the keyword. The seventh call site passes
    NEITHER keyword, and that one is the inventory row the paragraph below is about.
    Every number here is DERIVED rather than counted by eye, by an `ast` sweep over
    every `_unreadable(...)` call with its enclosing function and its keyword set,
    kept as `logs/builder-80de-r1-red.py` PART A (`-red-post.log`) so the next
    reader re-runs it instead. The default is the silent side, so a reader added
    later inherits the byte and not a claim it has not earned. Measured
    (`red-579d-r3-escape-slot-and-subject.py` PART E/F,
    the round-2 review's PART D/E before it): `_undecodable_role_json` reddens on
    ANY role JSON, so an UNDELIVERED `files/traefik-dynamic.json` was being told
    "the provisioner SAVES this file ... so the dashboard it serves is not the one
    on disk" — of a file no task delivers, that no provisioner opens, and that is
    not a dashboard. It is the class the neighbouring `_dashboard_sources_on_disk`
    docstring keeps its key set narrow for.

    A RENDERED file is never the file the engine reads, even when it is delivered:
    ansible renders it and the provisioner reads the RENDERED dest, at another path
    and another offset. That reason is right and the SUFFIX was the wrong test for
    it — ansible keys on the MODULE and not on the filename. Measured with a real
    `ansible-playbook` (core 2.21.1, `red-579d-r4-second-byte-and-template.py` E1,
    the round-3 review's PART E before it): `ansible.builtin.template:` with
    `src: dash.json` renders it, `{{ 40 + 2 }}` arriving as `42`. Both directions
    cost a sentence — a `template:`-delivered `.json` was told about a provisioner
    that never opens it, and a `copy:`-delivered `.json.j2`, whose bytes reach the
    dest verbatim, was denied the clause it had earned (F2/G2 of the same run).
    So the caller passes the fact `_delivered_dashboards` computes, and this
    function no longer reads the name.

    AND THAT IS A SECOND WITHHOLD REASON, WHICH NEEDS A SECOND SENTENCE. `rendered=`
    is a separate keyword from `provisioned=` because widening WHICH CALLERS reach a
    branch widens the claim its text makes, exactly as widening which FILES did one
    round earlier — and the text is not touched, so it is easy to miss. While the
    silent branch had ONE caller (the inventory row, keyed on no delivery) "…is
    claimed by the rows keyed on a DELIVERY, and this is not one" was true; routing
    the six delivery call sites that pass `rendered=` into it whenever the file is
    rendered made it false about the row printing it, and pointed the operator at a
    claim no row in the run makes — nothing here reads the rendered dest. THE UNIT IS
    THE CALL SITE HERE TOO: five of the six are test rows and the sixth is the same
    HELPER `_delivered_dashboard_documents` the paragraph above names, and an earlier
    spelling of this sentence said FIVE for the reason that one did. So the rows that
    can PRINT this withhold are the five routing directly plus the seven that read the
    helper's `problems` — twelve, which is what makes the count below a possible one:
    a five-reader routing could not have printed eleven. Every number here but that
    measured 11/1 is DERIVED by the same `ast` sweep as the paragraph above, kept as
    `logs/builder-80de-r2-red.py` PART A (`-red-post.log`), whose numbers this text is
    BUILT from. Measured end to end on a real
    `template:` delivery of a dashboard carrying one bad byte, guard run over a
    tempdir copy (the round-4 review's PART F, `red-579d-r5-save-layer-and-subject.py`
    PART G): 11 rows keyed on a DELIVERY printed it against the 1 that had earned it.
    So a DELIVERY reader withholding for the rendering says so, and only the reader
    that is not keyed on a delivery says it is not keyed on one.

    THE THIRD SENTENCE: A FILE THAT PARSES STILL HAS TO BE SAVED. `_json_string_open_at`
    answers the PARSE layer — does Go substitute here, or is this a syntax error — and
    the sentence above is a claim about the whole provisioner. A substituted document
    then meets the SAVE layer, whose rules this file already holds and already measured
    for the ordinary readable case (`_grafana_short_uid_defect` and friends, 3000 lines
    down). Measured on the pinned `grafana/grafana:13.1.0`, one delivered file per
    carrier in ONE provisioning run, HTTP API readback plus the container log
    (`red-579d-r5-save-layer-and-subject.py` PART A, the round-4 review's own PART A
    before it): a `0xb0` at a rune position inside the top-level `uid` is REFUSED —
    `msg="failed to save dashboard" error="uid contains illegal characters"` — as is a
    48-character tag plus one (51 bytes once substituted), while the SAME byte in the
    `title`, in a KEY string, and in a 47-character tag (50 bytes) are all SAVED in that
    same run. One row printed "the provisioner SAVES this file" for all of them, and
    that is DEC-160's own harm one layer over: the operator is sent to the Grafana UI to
    compare a dashboard that was never served, when the repair is in the container log —
    on a THIRD line, `failed to save dashboard`, that neither of the first two names.

    ASKING THOSE PREDICATES ANYTHING REQUIRES THE ENGINE'S DECODER, WHICH IS NOT
    PYTHON'S. See `_grafana_saved_bytes`: Go substitutes per invalid BYTE and python's
    `errors="replace"` per maximal SUBPART, and the two differ on every truncated
    multi-byte prefix — inert for the uid character class, load-bearing for both byte
    counts. The substitution stays inside this reporting function, on bytes no other row
    holds, which is what keeps it clear of the loader-wide policy DEC-150 refused.

    AND THE LOG LINE IS A PROPERTY OF THE RULE, NOT OF THE BRANCH THAT CATCHES IT. The
    third sentence's grep is its operational half, so getting it wrong costs what a wrong
    reason costs — the operator greps a line that is not in the log. Assigning it per
    branch (everything the `except` caught was the LOAD line, everything a predicate
    returned was the SAVE line) is wrong in BOTH directions, measured with every priced
    rule carried twice in ONE provisioning run (`logs/red-579d-r6-rule-to-log-line.py`
    PART A, and the round-5 review's `critic-579d-r5-rule-to-log-line.py` for the first
    two): a number past the IEEE double range is CAUGHT here and is a `failed to save
    dashboard`, while the whole `MustString()`-is-empty title class is RETURNED by a
    predicate and is a `failed to load dashboard from`. So `GrafanaUnprovisionableJSON`
    learns its line at the `raise`, where the rule was measured, and the load-layer title
    rule is asked here by `_grafana_dashboard_title` — which is NOT the `isinstance` test
    it looks like, because the empty string is a `str` and lands on the LOAD line while a
    whitespace-only title is a `str` and does not.

    IT IS ASKED FIRST FOR THE SAME REASON THE ENGINE ASKS IT FIRST. A document carrying
    BOTH an absent title and an illegal uid is refused at the LOAD, on the title (r6
    A-order/F1) — an `or` chain opening with the uid would name a rule the engine never
    reached, and the wrong line with it.

    AND THAT IS A CLAIM ABOUT THE WHOLE CHAIN, NOT ABOUT ONE `if`. Getting it right inside
    the `else:` alone left the ONE save-line rule that arrives as an EXCEPTION — the number
    range — asked before everything, because a `try` answers with whatever it catches. On a
    delivered dashboard carrying `1e400` and an empty title, 11 of 12 rows sent the operator
    to `failed to save dashboard` and none named the line the engine printed (r6 review F1 /
    r7 PART F). So the number rule is DEFERRED by the parse helper and asked in its measured
    place, and the six rules are asked in the engine's own order — which is the table above
    `GRAFANA_LOG_SAVE`, and which is NOT the order the review handed over: the number is 5th,
    ahead of the tag bound and behind everything else.

    AND AN ORDER IS ONLY MEASURED WHERE THE CARRIER COMBINES THE TWO RULES BEING ORDERED.
    The chain's own first two entries were wrong for two rounds because they were read off
    each rule's answer against the NUMBER — a shared pivot, which orders every rule against
    the pivot and nothing among the rest. Carried instead (`red-579d-r8-title-before-uid.py`
    PART A, the round-7 review's battery before it): the engine trims and checks the TITLE
    before it validates the `uid`, so the title is asked first here, and the uid's own two
    sub-rules are ordered by a uid carrying BOTH — the charset is asked before the length.

    ONE PREDICATE IS ASKED TWICE, AND THE SPLIT IS WHAT SITS IN THE ENGINE'S SLOT.
    `_grafana_short_uid_defect` is four rules under one name and only TWO of them are
    refusals: a NON-STRING uid and a uid that is only the engine's trim class are SAVED
    under a GENERATED uuid, at an address nothing in this repo can name (calibration
    C2). So the chain below asks the REFUSING half — `isinstance(uid, str) and
    _grafana_stored_uid(uid) is not None`, which is the whole line between the halves —
    in the engine's 4th slot, and the WHOLE predicate LAST, after the tag, paired with
    `log=None`. The substitution cannot MANUFACTURE the non-string class (substituting
    inside character positions cannot change a value's TYPE, and only a mangled KEY can
    make `uid` absent), but a delivered file carries it as authored, and the chain now
    NAMES it instead of yielding None at a fence and dropping it (task-1785624345-a15c,
    `logs/builder-a15c-red.py` PART A/C `d1_nonstruid_alone`).

    EVERY MESSAGE THE THIRD SENTENCE CAN PRINT IS STILL A REFUSAL — by the `log is None`
    split, and not by a member nothing consults. Those two members are the one entry the
    engine prints NO line for, so they are read by a FOURTH sentence of their own
    (`refused is not None and log is None`, below): the file IS saved, and what is wrong
    with it is the ADDRESS. The second sentence is not that sentence — it names the
    BYTES the engine substituted and says nothing about the address.

    ONE caller of `_read` still SKIPS rather than reports — the datasource-type
    census — and it keeps the accept path an unopenable file has always had,
    because a DELIVERED file it cannot decode is already named by the parse rows
    above it. `_dashboard_sources_on_disk` is the other direction and must not
    skip: see `_undecodable_role_json`.

    AND THE CLASS IS THE FILE'S, NOT THE FIRST BYTE'S. `_read` fails at the FIRST
    invalid sequence, so classifying `exc.start` alone answered for one byte while
    the sentence spoke about the file. The engine reads the WHOLE file: measured on
    the pinned `grafana/grafana:13.1.0`, three multi-byte carriers as one delivered
    file each in ONE provisioning run with the anti-vacuity pair in it
    (`red-579d-r4-second-byte-and-template.py` PART A/B, and the round-3 review's
    `logs/critic-579d-r3-second-byte-and-render.py` before it), a `0xb0` at a rune
    position in the `title` PLUS a `0xa0` in the structural whitespace before the
    final brace is REFUSED whole (`failed to load dashboard from` in that run's
    container log) — while both bytes at rune positions is SAVED, and the same pair
    in the other order is REFUSED. One bad byte outside a character position
    refuses the file however many are inside one, so the walk below classifies
    EVERY invalid sequence and the engine clause is `all()` of them. The origin
    this is measured from — a latin-1 save of `°` — mangles every non-ASCII byte in
    the file, and a U+00A0 in pasted indentation is the ordinary way the second one
    lands outside a string.

    THE SENTENCE NAMES THE BYTE ITS CLASS BELONGS TO. The first bad byte is what an
    operator's editor lands on, so it is still what the sentence opens with; but
    when the classes disagree, the byte that DECIDES is a different one and saying
    "byte 1598 is not a character position" of a byte inside a string would be a
    second false sentence in place of the first.
    """
    try:
        raw = path.read_bytes()
    except OSError:
        return "missing"
    # Every invalid sequence, walked from the end of the last one: `exc.start` and
    # `exc.end` are relative to the slice being decoded, so both are re-based onto
    # `raw`. `exc.end > exc.start` always, so the walk terminates.
    offsets, named, start = [], None, 0
    while True:
        try:
            raw[start:].decode("utf-8")
        except UnicodeDecodeError as exc:
            offsets.append(start + exc.start)
            if named is None:
                seq = bytes(exc.object[exc.start:exc.end])
                named = (f"not valid UTF-8 at byte {start + exc.start} "
                         f"({seq.hex(' ')}: {exc.reason})")
            start += exc.end
        else:
            break
    if named is None:
        return "missing"
    inside = [_json_string_open_at(raw, at) for at in offsets]
    rune = all(inside)
    if rune:
        where = ("the byte is INSIDE a JSON string" if len(offsets) == 1 else
                 f"all {len(offsets)} of them are INSIDE a JSON string")
    else:
        subject = ("the byte is" if len(offsets) == 1 else
                   f"byte {offsets[inside.index(False)]} is")
        where = (f"{subject} not a character position — it is outside every JSON "
                 f"string, or in an escape slot where JSON requires a specific ASCII "
                 f"byte")
    more = ("" if len(offsets) == 1 else
            f", and {len(offsets) - 1} more invalid sequence(s) at byte(s) "
            f"{', '.join(str(at) for at in offsets[1:])}")
    # The SAVE layer, asked only where the engine gets that far: the file has to be
    # keyed on a delivery, the bytes on disk have to be the bytes it reads, and the
    # parse has to survive them. `refused` is None when it serves this dashboard.
    refused = log = None
    if provisioned and not rendered and rune:
        # THE NUMBER RULE IS **DEFERRED**, NOT CAUGHT HERE, because a `try` answers with
        # whatever it catches and the engine reaches this rule 5th of six. See the order
        # table above `GRAFANA_LOG_SAVE`: everything the `except` below still catches — a
        # syntax error, a bare token — the engine really does reach first.
        deferred = []
        try:
            doc = _grafana_provisionable_json(_grafana_saved_bytes(raw), deferred=deferred)
        except json.JSONDecodeError as exc:
            # A syntax error is Go's scanner refusing the file, which is the LOAD (r6
            # A-syntax). Python's own exception carries no line, so this branch names it.
            refused, log = f"{exc}", GRAFANA_LOG_LOAD
        except GrafanaUnprovisionableJSON as exc:
            # …and this one does NOT name a line, because the rules it covers do not share
            # one: the exception learns it at the `raise`, where it was measured.
            refused, log = f"{exc}", exc.log
        else:
            if isinstance(doc, dict):
                uid, title = doc.get("uid"), doc.get("title")
                if not _grafana_dashboard_title(title):
                    # THE LOAD-LAYER RULE, AND IT IS ASKED FIRST BECAUSE THE ENGINE ASKS IT
                    # FIRST. A document with BOTH an empty `MustString()` title and an
                    # illegal `uid` is refused on the title, on the LOAD line, before any
                    # save-time validation runs — so an `or` chain that opened with the uid
                    # would name a rule the engine never reached and the wrong line with it
                    # (r6 A-order/F1, one delivered file in the same run as the rest).
                    #
                    # AND IT PRINTS THE LOAD LAYER'S OWN SENTENCE. Borrowing
                    # `_grafana_title_defect`'s text named the save-time TRIM — "empty after
                    # the ENGINE's trim … refuses to save it" — one clause before sending the
                    # operator to the LOAD line, and for `""` the trim is exactly the rule the
                    # engine never reached: it is empty BEFORE the trim, which is the whole of
                    # `_grafana_dashboard_title`'s discriminator (r6 review F2, r7 PART E).
                    refused = (f"title {title!r} is what Grafana's `MustString()` yields \"\" "
                               "for, so the provisioner refuses the file at the LOAD — "
                               "`Dashboard title cannot be empty` — BEFORE any save-time "
                               "validation runs, so a second defect on this document is not "
                               "the one to repair first (r6 A-title*, r7 A-order)")
                    log = GRAFANA_LOG_LOAD
                else:
                    # THE SAVE LAYER, IN THE ORDER THE ENGINE VALIDATES IT: the title's trim
                    # and its byte bound, then the `uid`, then the number the parse deferred,
                    # then the tags. Every adjacent pair here is carried by a delivered file
                    # of its own — which is what the first two entries were NOT, and why they
                    # were the wrong way round for two rounds. `red-579d-r7-rule-order.py`
                    # combined each rule with the NUMBER, which orders all of them against
                    # the number and NOTHING against each other; "3rd the uid, 4th the title"
                    # was read off that and is an inference wearing a measurement's clothes.
                    # Measured (`logs/red-579d-r8-title-before-uid.py` PART A, one delivered
                    # file per carrier in ONE run on the pinned image, container log kept,
                    # the round-7 review's own battery before it): an illegal `uid` with a
                    # blank-after-trim title is `Dashboard title cannot be empty`, an illegal
                    # `uid` with a 5001-character title is the 5000 bound, and a uid TOO LONG
                    # with a blank title is the title again — the uid rule named nowhere for
                    # any of the three, while uid + a 51-byte tag IS the uid. Anti-vacuity in
                    # that same run: each rule alone is reached and named (PART B 6/6).
                    #
                    # The number's place is the row the round-6 review handed over as "asked
                    # LAST" and named `tags` as the pair it could not separate — measured, it
                    # is asked BEFORE the tags, and a chain built from the handover would
                    # name the tag rule for a document the engine refuses on the number.
                    # Each entry carries its own line for the reason the exception does: the
                    # line is a property of the rule, and these four happen to agree — which
                    # is exactly why the FIFTH does not, below.
                    #
                    # AND THE uid LINK IS **TWO HALVES**, ONLY ONE OF WHICH IS A REFUSAL —
                    # the same split `test_delivered_dashboards_parse_as_dashboards` carries
                    # at :5362, this order's SECOND spelling. `_grafana_short_uid_defect` is
                    # four rules under one name and TWO of them are not refusals at all: a
                    # NON-STRING uid and a uid that is only the engine's trim class are SAVED
                    # under a GENERATED uuid, which the predicate's own returned sentence
                    # says verbatim ("the provisioner does not refuse it, it GENERATES a
                    # uuid"). `if isinstance(uid, str)` is HALF the line between the halves,
                    # so it got both non-refusing members wrong IN OPPOSITE DIRECTIONS: the
                    # trim-class member is a `str`, so it was asked 2nd — ahead of a rule the
                    # engine really stopped on — while the non-string member yielded None
                    # here and NOTHING re-asked the predicate, so the chain named no defect
                    # at all and the row fell through to its "SAVES this file" clause.
                    # `_grafana_stored_uid(uid) is not None` is the whole line: None for both
                    # non-refusals, a string for both refusals, so no member is asked twice
                    # and none is dropped.
                    #
                    # Measured, and on THIS chain's own carriers, which are a separate
                    # delivered-file set from the other spelling's — this code runs only for
                    # a delivered dashboard `_read` cannot decode as UTF-8 whose bad byte is
                    # at a SAVED position, so every file below carries a raw `0xff` inside a
                    # JSON string (`logs/builder-a15c-red.py` PART A/C/D/E, one delivered
                    # file per ADJACENT PAIR in ONE provisioning run on the pinned
                    # `grafana/grafana:13.1.0`, container log kept, every `error=` printed,
                    # `/api/search` read back; `logs/critic-fb36-r2-unreadable-sibling.py`
                    # named the defect before it): a trim-class uid with `1e400` is the
                    # NUMBER at the engine and with a 51-byte tag is the TAG, and each
                    # non-refusing member ALONE is IN THE STORE afterwards — which is what
                    # makes them non-refusals rather than refusals a run failed to trigger.
                    # Anti-vacuity in that same run: the legal control is served and each of
                    # the five rules ALONE is reached and named (PART B).
                    #
                    # SO THE REFUSING HALF IS ASKED 4TH AND THE OTHER TWO LAST, AFTER THE TAG
                    # — AN ORDERING, NEVER A DELETION (mem: flip a guard's polarity, never
                    # delete it). The engine saving a dashboard at an address nothing in this
                    # repo can name is a real defect and this chain stays RED for it; it is
                    # simply not a refusal, so it cannot outrank a rule the engine did stop
                    # on. AND ITS LINE IS `None`, WHICH IS THE THIRD CLAIM THIS CHAIN MAKES:
                    # every other entry pairs its rule with a container-log line because the
                    # engine printed one, and for these two the engine printed NOTHING and
                    # SERVED the file. Carrying `GRAFANA_LOG_SAVE` here would send the
                    # operator to grep a line that does not exist and frame a SAVE as a
                    # refusal — the clause below reads the `None` and says what was measured
                    # instead (PART D: `failed to save dashboard` was the row's answer for a
                    # trim-class uid ALONE, for a file `/api/search` returns).
                    number = deferred[0] if deferred else None
                    refuses_uid = (isinstance(uid, str)
                                   and _grafana_stored_uid(uid) is not None)
                    for refused, log in (
                            (_grafana_title_defect(title), GRAFANA_LOG_SAVE),
                            (_grafana_short_uid_defect(uid) if refuses_uid else None,
                             GRAFANA_LOG_SAVE),
                            (None if number is None else f"{number}",
                             GRAFANA_LOG_SAVE if number is None else number.log),
                            (_grafana_tags_defect(doc.get("tags")), GRAFANA_LOG_SAVE),
                            (_grafana_short_uid_defect(uid), None)):
                        if refused is not None:
                            break
            else:
                # The three predicates take FIELDS, so a document that is not an object
                # cannot be asked — and falling through to "SAVES" would be a third false
                # sentence for the shape's sake. Measured in the same run as the rest
                # (`red-579d-r5-save-layer-and-subject.py` A-toparray): a `0xb0` at a rune
                # position inside a top-level ARRAY is REFUSED, on the LOAD line — and the
                # engine's error there is `Dashboard title cannot be empty` (r6 A-toparray),
                # which is the load-layer rule above reading a document that has no fields
                # to read. Same line, same check, one shape further out.
                refused = (f"the top level is {type(doc).__name__} and not an object, so "
                           "there are no dashboard fields to read — the provisioner refuses "
                           "the file (red-579d-r5 A-toparray, r6 A-toparray)")
                log = GRAFANA_LOG_LOAD
    if not provisioned:
        clause = (f"{where}, and this row names the byte only: what an engine does "
                  f"with these bytes is claimed by the rows keyed on a DELIVERY, "
                  f"and this is not one")
    elif rendered:
        clause = (f"{where}, and this row names the byte only: `ansible.builtin.template:` "
                  f"RENDERS this file, so the bytes any engine reads are at the dest and "
                  f"not here — a path nothing in this guard opens")
    elif refused is not None and log is None:
        # THE CHAIN'S LAST ENTRY, WHICH IS THE ONE RULE THAT IS NOT A REFUSAL. `log is None`
        # is the entry's own statement that the engine printed no line, and this branch is
        # what makes that a sentence rather than a silence: the file IS saved, so "refuses
        # to serve" and "look for `failed to save dashboard`" would both be false of it —
        # measured on the pinned image, `/api/search` returns these documents in the same
        # run that refuses the four rules above them (`logs/builder-a15c-red.py` PART A/B).
        # What IS wrong with them is still worth the operator's RED: the address is one the
        # engine invented, so no line in this repo can find the dashboard again, and the
        # bytes it serves are not the bytes on disk either.
        clause = (f"{where}, so the provisioner substitutes U+FFFD for each of them and "
                  f"PARSES the file — and then SAVES the document it holds, at an address "
                  f"nothing in this repo can name: {refused} — so there is NO line in the "
                  f"container log for this file, and what the Grafana UI serves is neither "
                  f"the bytes on disk nor a dashboard any uid here will find")
    elif refused is not None:
        clause = (f"{where}, so the provisioner substitutes U+FFFD for each of them and "
                  f"PARSES the file — and then refuses to serve the document it holds: "
                  f"{refused} — so look for `{log}` in the container log, not for this "
                  f"dashboard in the Grafana UI")
    elif rune:
        clause = (f"{where}, where the provisioner SAVES this file with those bytes "
                  f"replaced by U+FFFD, so the dashboard it serves is not the one "
                  f"on disk")
    else:
        clause = (f"{where}, where it is a syntax error and not a substitution — the "
                  f"provisioner REFUSES the whole file (`failed to load dashboard "
                  f"from` in the container log) and serves no dashboard from it at all")
    return f"{named}{more} — {clause}"


def _yaml_unquote(scalar: str) -> str:
    """A scalar with a trailing comment and surrounding quotes removed."""
    scalar = scalar.strip()
    if scalar.startswith(("'", '"')):
        quote = scalar[0]
        end = scalar.find(quote, 1)
        if end != -1:
            return scalar[1:end]
    return scalar.split(" #")[0].strip()


def _norm_path(path: str) -> str:
    """Quotes stripped and `{{ var }}` spacing collapsed, so two spellings compare."""
    return re.sub(r"\{\{\s*(.*?)\s*\}\}", r"{{\1}}", _yaml_unquote(path))


def _task_blocks(body: str) -> list:
    """Every column-0 task of an Ansible task file as (name, block).

    A task file's document root is a list, so its entries live at column 0; the
    block runs from its `- name:` line to the next column-0 list entry. Slicing
    this way is what keeps a neighbouring task's `mode:` from answering for
    this one — the way a whole-file grep for `mode: "0640"` would be vacuous
    here, since eight tasks in this file carry that string.
    """
    out = []
    for m in re.finditer(r"(?m)^-\s+name:\s*(.+?)\s*$", body):
        nxt = body.find("\n- ", m.end())
        out.append((_yaml_unquote(m.group(1)), body[m.start(): nxt if nxt != -1 else len(body)]))
    return out


def _scalar(block: str, key: str) -> str | None:
    """`key: value` read from a task block, or None.

    Anchored on a line whose first non-space token is the key, so an inline
    `- { src: x, dest: y }` loop entry cannot answer for a task-level `src:`.
    """
    m = re.search(rf"(?m)^\s*{re.escape(key)}:\s*(\S.*?)\s*$", block)
    return _yaml_unquote(m.group(1)) if m else None


def _loop_items(block: str) -> list:
    """The plain scalar entries of a task's `loop:`."""
    m = re.search(r"(?m)^(\s*)loop:\s*$", block)
    if not m:
        return []
    items = []
    for line in block[m.end():].splitlines():
        if not line.strip():
            continue
        entry = re.match(r"^\s*-\s+(\S.*?)\s*$", line)
        if not entry:
            break
        items.append(_yaml_unquote(entry.group(1)))
    return items


def _mode_bits(mode: str | None) -> int | None:
    """`"0750"` -> 0o750. Anything else (symbolic, Jinja, absent) -> None.

    A mode this cannot decode is reported by the callers as unreadable rather
    than skipped: `mode: u=rwx,g=rx` is a legal ansible spelling and a guard
    that quietly passed it would be green over the very thing it checks.
    """
    if mode is None:
        return None
    m = re.fullmatch(r"0?([0-7]{3})", mode.strip())
    return int(m.group(1), 8) if m else None


def _grants_access(mode_bits: int, owner: str | None, group: str | None, need_exec: bool) -> tuple:
    """Does (owner, group, mode) grant read [+traverse] to uid 472, gid {0}?

    A plain POSIX evaluation against the MEASURED identity, deliberately not a
    literal-mode comparison: `0750 root:root` passes on the group bit (gid 0 is
    in the identity's groups) and `0644 root:root` passes on the other bit, so
    this states the property without forbidding either spelling. `root` and `0`
    are both accepted as the gid-0 name because ansible accepts both.
    """
    want = 5 if need_exec else 4
    owner_id = {"root": 0, "0": 0, "grafana": GRAFANA_UID, str(GRAFANA_UID): GRAFANA_UID}.get(
        (owner or "").strip())
    group_id = {"root": 0, "0": 0}.get((group or "").strip(), None)
    if owner_id == GRAFANA_UID and ((mode_bits >> 6) & want) == want:
        return True, "owner"
    if group_id in GRAFANA_GIDS and ((mode_bits >> 3) & want) == want:
        return True, "group"
    if (mode_bits & want) == want:
        return True, "other"
    return False, f"owner={owner} group={group} mode={oct(mode_bits)[2:]:0>4}"


def _directory_declarations(body: str) -> dict:
    """path -> (task name, mode, owner, group) for every dir the role creates.

    `{{ item }}` paths are expanded over the task's own `loop:`, because the
    grafana dirs are created by a shared loop task and a reader that could not
    see through it would have nothing to check.
    """
    out = {}
    for name, block in _task_blocks(body):
        if not re.search(r"(?m)^\s*ansible\.builtin\.file:\s*$", block):
            continue
        if _scalar(block, "state") != "directory":
            continue
        raw = _scalar(block, "path")
        if raw is None:
            continue
        raw = _norm_path(raw)
        mode, owner, group = _scalar(block, "mode"), _scalar(block, "owner"), _scalar(block, "group")
        paths = ([raw.replace("{{item}}", item) for item in _loop_items(block)]
                 if "{{item}}" in raw else [raw])
        for path in paths:
            out[path] = (name, mode, owner, group)
    return out


def _delivered_dashboards(body: str) -> list:
    """(task name, src on disk or None, dest, RENDERED) for every file put in the mount.

    THE INVENTORY. Keyed on the DEST — anything the role copies or renders into
    `{{ docker_host_project_dir }}/grafana/dashboards/` is a dashboard Grafana
    will load, whichever module put it there — so a dashboard added by Step 4b
    or 4c is inside this check the moment its delivery task exists, and cannot
    be added to the check's coverage only by remembering to.

    A delivery with no `src:` is REPORTED (src None), not skipped. It is a real
    ansible spelling — `ansible.builtin.copy` with an inline `content:` — and
    while it was skipped, a dashboard written that way was invisible to the
    cross-file uid check while the guard stayed green: exactly the silent skip
    keying on the dest was supposed to make impossible. The callers fail on it,
    because a dashboard whose JSON lives inline in a task file is one no reader
    here can check, not one there is nothing to check about.

    A `dest:` NAMING THE DIRECTORY ITSELF is the same inventory, one spelling
    over, and is keyed on the filename ansible would give it. `copy:`/`template:`
    onto an existing directory writes the src under its own basename, so
    `dest: …/grafana/dashboards` delivers a dashboard exactly as a full path
    does — and a dest-keyed reader that demanded the `/` matched neither. It is
    not hypothetical bookkeeping: measured on the real tree
    (`logs/rework-step04b-r2-dest-dir-probe.log`), a third dashboard duplicating
    the PVE dashboard's uid at that dest is guard GREEN 13/13 when its filename
    also misses the sibling inventory's `files/*dashboard*.json` glob (row D2) —
    the identical silent collision as the `.j2` skip, through the other reader.

    THE FOURTH FIELD IS THE MODULE, AND IT IS PUBLISHED BECAUSE A CALLER NEEDS IT.
    `is_template` decides which root the src resolves under, and it was computed
    and thrown away here while `_unreadable` re-derived the same fact from the
    SUFFIX one caller over — a proxy ansible does not enforce. Measured with a
    real `ansible-playbook` (core 2.21.1, `red-579d-r4-second-byte-and-template.py`
    E1): `ansible.builtin.template:` with `src: dash.json` RENDERS it, `{{ 40 + 2 }}`
    arriving at the dest as `42`. So the suffix answers neither direction, and the
    fact this function already holds answers both — it is the delivery MODULE, not
    the filename, that decides whether the bytes on disk are the bytes an engine
    reads. Published as a fourth element rather than passed by a second scan so
    the two readings cannot drift apart.
    """
    out = []
    for name, block in _task_blocks(body):
        dest = _scalar(block, "dest")
        if dest is None:
            continue
        dest = _norm_path(dest)
        src = _scalar(block, "src")
        is_template = re.search(r"(?m)^\s*ansible\.builtin\.template:\s*$", block) is not None
        if dest.rstrip("/") == DASHBOARDS_DIR:
            # The implied filename, so the dest half of the collision check still
            # compares like with like. With no `src:` there is no basename to
            # imply, and the dir itself is carried through to be REPORTED below
            # rather than dropped.
            if src is not None:
                dest = f"{DASHBOARDS_DIR}/{src.rsplit('/', 1)[-1]}"
        elif not dest.startswith(DASHBOARDS_DIR + "/"):
            continue
        if src is None:
            out.append((name, None, dest, is_template))
            continue
        root = TEMPLATES if is_template else FILES
        out.append((name, root / src, dest, is_template))
    return out


def _grafana_file_deliveries(body: str) -> list:
    """(task name, dest, mode, owner, group) for every file the role puts under grafana/."""
    out = []
    for name, block in _task_blocks(body):
        dest = _scalar(block, "dest")
        if dest is None:
            continue
        dest = _norm_path(dest)
        if not dest.startswith(f"{PROJECT_DIR}/grafana/"):
            continue
        out.append((name, dest, _scalar(block, "mode"), _scalar(block, "owner"), _scalar(block, "group")))
    return out


def _compose_service_block(body: str, service: str) -> str:
    """The compose service block, sliced to the next key at its own indent."""
    m = re.search(rf"(?m)^(\s+){re.escape(service)}:\s*$", body)
    if not m:
        return ""
    indent = len(m.group(1))
    rest = body[m.end():]
    nxt = re.search(rf"(?m)^\s{{0,{indent}}}\S", rest)
    return rest[: nxt.start()] if nxt else rest


def _mount_source(block: str, target: str) -> str | None:
    """The host side of the `volumes:` entry whose container side is `target`."""
    for line in block.splitlines():
        # `(.+?)`, not `(\S+)`: the host side is a Jinja expression carrying
        # spaces (`{{ docker_host_project_dir }}/grafana/dashboards:...`), so a
        # non-space match would read no mount in this file at all.
        entry = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if not entry or ":" not in entry.group(1):
            continue
        parts = entry.group(1).split(":")
        opts = parts[-1] if parts[-1] in ("ro", "rw", "z", "Z") else None
        fields = parts[:-1] if opts else parts
        if len(fields) >= 2 and fields[-1] == target:
            return _norm_path(":".join(fields[:-1]))
    return None


def _duplicate_mapping_keys(body: str) -> list:
    """Every mapping key this file defines TWICE in one mapping, at any depth.

    Step-4a F1, round 3 (F2). Grafana parses provisioning with go-yaml v3, which
    treats a duplicate key as a HARD ERROR and not as last-wins, and the whole
    server dies on it — not just the file. Measured on grafana/grafana:13.1.0,
    four rows and a control (`logs/red-step04a-r3-battery.log` leg K):

        K0  the delivered pair                                 HEALTHY (control)
        K1  a second top-level `datasources:`   (datasource.yml)   exit 1
        K2  a second top-level `providers:`     (dashboards.yml)   exit 1
        K3  a second top-level `apiVersion:`    (datasource.yml)   exit 1
        K4  a second `name:` INSIDE one entry   (datasource.yml)   exit 1

    Each dies with `yaml: unmarshal errors: … mapping key … already defined`.
    K3 and K4 are why this scans every key at every depth rather than the two
    list keys the other checks happen to read: the class is the PARSER's, so
    bounding it at the keys this guard cares about would leave the file's own
    `apiVersion` and every entry's own keys able to kill the server while the
    guard printed PASS. That state is exactly the one this check exists to
    exclude — the round-1 fail-open ("rc=0 on a tree that will not boot"), one
    key over.

    A LINE THIS SCANNER CANNOT READ IS REPORTED, NOT SKIPPED, per the repo rule:
    it understands block mappings and block sequences of plain scalars, which is
    all these two templates contain. A flow mapping (`{a: 1}`), a block scalar
    (`|`, `>`) or an anchor arrives as `<UNREADABLE …>` and reddens, because a
    reader that shrugged past it would be answering "no duplicates" about a file
    it did not read.

    THE VALUE SIDE IS WHY THAT RULE IS SPELLED OUT TWICE. The first version of
    this scanner read `options: {path: /x}` as an ordinary key with an opaque
    scalar value, which is true of the LINE and false of the FILE: a duplicate
    inside the flow mapping (`{path: a, path: b}`) is just as fatal to the server
    and this reader could not see it. Battery row H6 caught that — the row went
    red for an unrelated check's reason while THIS check printed no problem — so
    a value that opens a flow collection, a block scalar or an anchor is
    unreadable rather than opaque. The price is that these two templates may not
    use flow style; it is loud, immediate, and it is the direction that cannot
    ship a server that will not boot.
    """
    dupes, stack = [], []
    for lineno, raw in enumerate(body.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#") or raw.strip() in ("---", "..."):
            continue
        m = re.match(r"^(\s*)((?:-\s+)*)([\w.\-]+):(?:\s+(\S.*)|\s*)$", raw)
        if m and m.group(4) and m.group(4)[0] in "{[|>&*!":
            dupes.append(f"line {lineno}: <UNREADABLE VALUE> {raw.strip()!r} — this reader "
                         "models block style only, and cannot see a duplicate key inside it")
            continue
        if not m:
            # A bare sequence scalar (`- foo`) defines no key and cannot collide;
            # anything else is a construct this scanner does not model.
            if not re.match(r"^\s*-\s+[^\s{\[&*|>][^:]*$", raw):
                dupes.append(f"line {lineno}: <UNREADABLE LINE> {raw.strip()!r}")
            continue
        indent, dashes, key = len(m.group(1)), m.group(2), m.group(3)
        depth = indent + len(dashes)
        if dashes:
            # A sequence item opens a FRESH mapping, so the same key appearing
            # once per entry (`- name:` on every datasource) is not a duplicate.
            while stack and stack[-1][0] >= depth:
                stack.pop()
            stack.append((depth, set()))
        else:
            while stack and stack[-1][0] > depth:
                stack.pop()
            if not stack or stack[-1][0] < depth:
                stack.append((depth, set()))
        if key in stack[-1][1]:
            dupes.append(f"line {lineno}: mapping key {key!r} already defined at this level")
        stack[-1][1].add(key)
    return dupes


def _provisioning_entries(body: str, key: str) -> list:
    """Each entry of a top-level provisioning list, as a dict of its scalars.

    `key` is anchored at column 0 with `(?m)^{key}:` so `datasources:` cannot be
    answered for by `deleteDatasources:` — the two lists live in the same file
    and the migration check reads both, so a reader that confused them would
    compare the block with itself and be green by construction.

    A key defined TWICE at column 0 returns [] — the FAIL-CLOSED half of round
    3's F2, and the reason it lives in the reader as well as in its own check.
    This used to take the first `re.search` hit and never ask whether there was
    a second, so a file the server refuses outright (battery row K1) was read as
    if the first list were the whole truth and every caller was green on it.
    Callers all redden on an empty list, and
    `test_provisioning_files_have_no_duplicate_key` prints the real reason.
    """
    if len(re.findall(rf"(?m)^{re.escape(key)}:\s*$", body)) > 1:
        return []
    m = re.search(rf"(?m)^{re.escape(key)}:\s*$", body)
    if not m:
        return []
    entries, current = [], None
    for line in body[m.end():].splitlines():
        if line.strip().startswith("#") or not line.strip():
            continue
        if re.match(r"^\S", line):
            break
        start = re.match(r"^\s*-\s+(\w+):\s*(\S.*?)\s*$", line)
        if start:
            if current is not None:
                entries.append(current)
            current = {start.group(1): _yaml_unquote(start.group(2))}
            continue
        kv = re.match(r"^\s+(\w+):\s*(\S.*?)\s*$", line)
        if kv and current is not None:
            current[kv.group(1)] = _yaml_unquote(kv.group(2))
    if current is not None:
        entries.append(current)
    return entries


def _datasource_entries(body: str) -> list:
    """(name, uid) for each entry of the provisioning file's `datasources:` list."""
    return [(e.get("name"), e.get("uid")) for e in _provisioning_entries(body, "datasources")]


def _datasource_types(body: str) -> dict:
    """uid -> the `type:` provisioned at it, for each `datasources:` entry.

    `_datasource_entries` above answers "which uids exist"; this answers "and
    what is each one", which is the other half of the same line in the same
    file. A uid whose entry declares no `type:` maps to None rather than being
    dropped, because "no type is provisioned here" and "this uid was never
    provisioned" are different states and the row below has to tell them apart:
    the first is a hole in the truth source and must be loud, the second belongs
    to `test_delivered_dashboards_reference_the_provisioned_uid`.
    """
    return {e["uid"]: e.get("type") for e in _provisioning_entries(body, "datasources")
            if e.get("uid")}


def _datasource_refs(node, path: str = "$") -> list:
    """Every datasource reference in a dashboard JSON, as (json path, uid, type).

    Walks the WHOLE document rather than the panel list: a target, an
    annotation, a template variable and a panel each carry their own
    `datasource`, and a check that read only `panels[]` would pass a dashboard
    whose queries all point somewhere else. The legacy string spelling
    (`"datasource": "Prometheus"`) is captured too — it is a NAME reference,
    which is exactly the confusion this file exists to catch, so it is reported
    with its raw value rather than dropped.

    ONE WALK, TWO QUESTIONS. The object spelling states a uid AND a type in the
    same three tokens, and the two are checked by two different rows below, so
    both are returned here rather than each row growing its own walker — two
    walkers over one grammar are two chances to disagree about what a carrier
    is. `type` is None for the string spelling (a NAME is not a type) and for an
    object that omits it.
    """
    refs = []
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}"
            if key == "datasource":
                if isinstance(value, dict):
                    kind = value.get("type")
                    refs.append((here, value.get("uid"),
                                 kind if isinstance(kind, str) else None))
                elif isinstance(value, str):
                    refs.append((here, value, None))
                else:
                    refs.append((here, None, None))
                continue
            refs += _datasource_refs(value, here)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            refs += _datasource_refs(item, f"{path}[{i}]")
    return refs


def _json_strings(node, path: str = "$") -> list:
    """Every string LEAF of a dashboard document, as (json path, text).

    THE CARRIER PROBLEM, ANSWERED THE OTHER WAY ROUND FROM
    `test_pve_panels_name_series_the_exporter_declares`. That check scans the RAW
    file because a series name reaches Prometheus from a panel `expr`, an
    annotation `expr`, a template variable's `query.query` and its `definition`,
    and enumerating those keys would go blind on the next one Grafana adds. This
    walks every string VALUE instead, which reaches the identical set — none of
    those carriers is anything but a JSON string — and closes the one bound the
    raw scan has to declare: a raw reader sees the file's ESCAPES, so
    `{service=\\"plex@file\\"}` on disk is not the text `{service="plex@file"}`
    and a selector check written against raw bytes would have to model JSON
    escaping to read its own subject. `json.loads` has already done that.

    It is NOT proposed as a repair to the `pve_*` row, which is settled at round
    6 (DEC-077) and whose subject — a bare metric NAME — carries no character
    JSON escapes. The selectors below carry quotes in every occurrence.
    """
    out = []
    if isinstance(node, dict):
        for key, value in node.items():
            out += _json_strings(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, item in enumerate(node):
            out += _json_strings(item, f"{path}[{i}]")
    elif isinstance(node, str):
        out.append((path, node))
    return out


# THE TWO CONTAINER-LOG LINES A REFUSAL LANDS ON, AND THEY BELONG TO THE **RULE**.
#
# `_unreadable` is the one function in this file that prints either of them, because it
# is the one that tells an operator where to go and look. Its first spelling assigned
# them by BRANCH — everything an `except` caught was the LOAD line, everything a
# save-layer predicate returned was the SAVE line — and the engine does not partition
# that way. Measured on the pinned `grafana/grafana:13.1.0`, EVERY priced rule carried
# twice (clean, and with a `0xb0` at a rune position) as one delivered file each in ONE
# provisioning run, the container log kept, with the anti-vacuity pair in that same run
# (`logs/red-579d-r6-rule-to-log-line.py` PART A, 14 rules x 2 spellings; the round-5
# review's `logs/critic-579d-r5-rule-to-log-line.py` found the first two):
#
#     SAVE   a number past the IEEE double range — `json: cannot unmarshal number 1e400
#            into Go value of type float64`. It is CAUGHT as an exception here and it is
#            a SAVE-line refusal, which is what makes the branch the wrong carrier.
#     SAVE   uid too long / uid outside the charset / a tag over 50 bytes / a title
#            empty AFTER the engine's trim / a title over 5000 bytes.
#     LOAD   a bare `NaN`/`Infinity` token, a syntax error, a top level that is not an
#            object — and the whole `MustString()`-is-empty class below.
#
# The clean and the byte-carrying spelling of each rule printed the SAME line (14/14),
# so the substitution is not the variable and the rule is.
#
# AND THE RULES HAVE AN ORDER, WHICH IS NOT THE ORDER A `try`/`except`/`else` IMPOSES.
# Assigning the line per rule is only half of it: a document breaks more than one rule at a
# time, and the operator is told to repair the rule the engine STOPPED on. Measured on the
# same pinned image, one delivered file per PAIR in ONE provisioning run, container log kept
# (`logs/red-579d-r8-title-before-uid.py` PART A and the round-7 review's
# `logs/critic-579d-r7-save-layer-order.py` for the save-layer pairs,
# `logs/red-579d-r7-rule-order.py` for each rule against the number, and the round-6
# review's `logs/critic-579d-r6-parse-vs-load-order.py` for the parse and the LOAD title):
#
#     1st  the parse — a syntax error or a bare token, LOAD. `NaN` + `1e400` -> `NaN`.
#     2nd  the LOAD-layer title, LOAD. `1e400` + a `MustString()`-empty title -> the title,
#          in all four spellings (empty, absent, null, a top-level array).
#     3rd  the save-time title trim and its 5000-byte bound, SAVE. An illegal uid + `"   "`
#          -> the title; an illegal uid + a 5001-character title -> the title; a uid TOO
#          LONG + `"   "` -> the title. `1e400` + either title spelling -> the title.
#     4th  the save-time `uid`, SAVE. `1e400` + an illegal uid -> the uid; an illegal uid +
#          a 51-byte tag -> the uid. Its two SUB-rules are ordered too, and the CHARSET is
#          asked first: a 43-character uid carrying a space is `uid contains illegal
#          characters`, in both positions of the illegal character (r8 PART A/E), while the
#          length rule ALONE is reached and named in that same run.
#     5th  THE NUMBER RANGE, SAVE.
#     6th  the tag bound, SAVE. `1e400` + a 51-byte tag -> `cannot unmarshal number`, and
#          the tag rule is what that same run's tag-alone carrier is refused on.
#
# EVERY ADJACENT PAIR ABOVE IS ITS OWN DELIVERED FILE, AND THAT IS THE POINT. Two rounds put
# the uid 3rd and the title 4th by reading both off their answers against the NUMBER — one
# shared pivot orders each rule against the pivot and orders nothing among the rest. The
# round-6 review handed over "the number rule is asked LAST" the same way (measured, it is
# asked BEFORE the tags: `logs/red-579d-r7-pre.log` A-num_tag is that prediction failing in
# the very run that priced it, and `logs/red-579d-r7-tag-vs-number.py` reproduces it), and
# round 7 then produced the uid/title ordinals by the identical method. So a rule ADDED here
# needs a carrier against its NEIGHBOURS, not against whichever rule is convenient.
GRAFANA_LOG_SAVE = "failed to save dashboard"
GRAFANA_LOG_LOAD = "failed to load dashboard from"


class GrafanaUnprovisionableJSON(ValueError):
    """A file Python's `json` reads and Grafana's provisioner refuses outright.

    Not a subclass of `JSONDecodeError`, because it is not a claim about the JSON
    grammar — `1e400` is valid JSON by any parser's grammar. It is a claim about the
    FIRST reader a delivered file meets, which is Go, and which is narrower.

    IT CARRIES THE CONTAINER-LOG LINE IT WAS RAISED FOR, because the line is a property
    of the RULE and the raise site is where the rule was measured. A caller that read it
    off the `except` instead would be answering for every rule this class covers at once,
    and the two it covers land on DIFFERENT lines (the block above). The default is the
    LOAD line: that is where a parse-layer refusal lands, and a refusal that has not
    named its own line has not been measured onto the other one.
    """

    def __init__(self, message, *, log=GRAFANA_LOG_LOAD):
        super().__init__(message)
        self.log = log


def _grafana_provisionable_json(raw: str, *, deferred: list | None = None):
    """The document a DELIVERED dashboard file becomes — or raise, because it never does.

    A DELIVERED FILE MEETS GO BEFORE IT MEETS A BROWSER, AND PYTHON IS LOOSER THAN
    BOTH. `json.loads` is the third parser in the chain and the most permissive one, so
    reading a delivery with it and stopping there accepts files that never become
    dashboards at all. Measured over the pinned `grafana/grafana:13.1.0` — the tag
    `defaults/main.yml` pins — with the repo's own file-provider shape, asked over
    Grafana's own HTTP API, in `logs/critic-step05d-r7-nonfinite-token.py` (23/23) and
    `logs/calibration-step05d-rework-r8-number-range.py` (18/18):

      * THE THREE BARE TOKENS. `NaN`, `Infinity` and `-Infinity` are not JSON — Python's
        parser invents them, `JSON.parse` refuses them and so does Go. The provisioner
        never loads the file: `invalid character 'I' in numeric literal`, 404.
      * A NUMBER PAST THE DOUBLE RANGE, IN EITHER SPELLING. Grafana unmarshals into
        `interface{}`, so every number becomes a `float64`, and one that does not fit
        is refused at the SAVE: `json: cannot unmarshal number 1000…000 into Go value
        of type float64`, 404. `1` followed by 400 zeros and `1e400` are the same value
        and the same 404 (calibration B2) — which is why this is a test on the LITERAL
        and not an `except OverflowError`, the only spelling of the two that Python
        raises for.
      * AND THE LINE IS THE RANGE, NOT THE LENGTH. `9007199254740993`, the largest int
        outside `Number.MAX_SAFE_INTEGER` but inside the double range, provisions 200,
        as does `1.7976931348623157e308` (calibration B4).

    THE SMALL END IS ACCEPTED, AND THAT IS MEASURED RATHER THAN OVERLOOKED. `1e-400` is
    a `strconv.ParseFloat` range error in exactly the way `1e400` is, and the engine
    LOADS that file (calibration B5) — so the class is one-sided and a detector written
    by symmetry would refuse a working dashboard. This is the accept side of that, and
    `logs/red-step05d-rework-r8.py` A7/B6 hold it.

    THE CALLERS ARE THE FIVE READERS OF A DELIVERED DASHBOARD, all of which already
    handle an unreadable delivery, so this adds no error path — only a shared rule.
    `_dashboard_sources_on_disk` deliberately does NOT call it: that one asks whether a
    file on disk IS a dashboard, and a dashboard the provisioner would refuse is still
    one. Narrowing it would hide an undelivered broken file from
    `test_dashboard_delivery_inventory_is_complete` rather than report it (r8 F1/F2).

    `deferred=` IS FOR THE ONE CALLER THAT HAS TO NAME **WHICH** RULE REFUSED THE FILE.
    Raising is right for the five readers above: they ask "is this a dashboard the
    provisioner loads", and any refusal answers it. `_unreadable` asks a different question
    — which rule, and therefore which container-log line — and the answer depends on the
    ORDER, because the number rule is the 5th of six and an exception is the 1st of
    anything. Passing a list collects the number refusal instead of raising it, so that
    caller can ask it in its measured place; the token and syntax refusals still raise,
    because they really are first. The default is unchanged and so is every other caller.
    """
    def _refuse_at_save(message: str, cast=None, literal=""):
        # THE NUMBER RULE IS A **SAVE**-LINE REFUSAL, and it is the one rule of this class
        # that is: the unmarshal happens as the dashboard is saved, so the log reads
        # `failed to save dashboard`, not the `failed to load dashboard from` the token
        # rule below earns (r6 A-numrange, and the docstring above, which said so first).
        # It is also the one the engine reaches LATE (the table above `GRAFANA_LOG_SAVE`),
        # which is why it is the one a caller can defer.
        exc = GrafanaUnprovisionableJSON(message, log=GRAFANA_LOG_SAVE)
        if deferred is None:
            raise exc
        deferred.append(exc)
        return None if cast is None else cast(literal)

    def _number(literal: str, cast):
        try:
            double = float(literal)
        except (OverflowError, ValueError):            # not reachable from JSON's grammar
            double = None
        if double is None:
            # Outside the `except` so no context is chained, which is what the `from None`
            # this replaced was for.
            return _refuse_at_save(f"the number {literal[:32]}… is not a double")
        if double in (float("inf"), float("-inf")):
            return _refuse_at_save(
                f"the number {literal if len(literal) < 32 else literal[:32] + '…'} is outside "
                "the IEEE double range, so Grafana's provisioner refuses to SAVE the dashboard "
                "(Go: cannot unmarshal number … into Go value of type float64)", cast, literal)
        return cast(literal)

    def _token(token: str):
        raise GrafanaUnprovisionableJSON(
            f"`{token}` is not JSON — Python's parser invents it, and Grafana's provisioner "
            "refuses to LOAD a file carrying it (Go: invalid character in numeric literal)",
            log=GRAFANA_LOG_LOAD)

    return json.loads(raw, parse_constant=_token,
                      parse_int=lambda literal: _number(literal, int),
                      parse_float=lambda literal: _number(literal, float))


def _delivered_dashboard_documents(body: str) -> tuple:
    """(label, parsed doc) for every delivered dashboard, plus what could not be read.

    The three checks below all ask a question of a dashboard's CONTENT, so they
    share one reader rather than three copies of the same loop — and one copy of
    the rule that a delivery this cannot read is REPORTED and not skipped. An
    inline `content:` delivery, a missing src and a file that is not JSON each
    arrive as a problem string; the callers redden on them even though the parse
    check next door prints the better reason. A check that read the content of
    SOME of the delivered dashboards could not answer for any of them.
    """
    docs, problems = [], []
    for name, src, _dest, rendered in _delivered_dashboards(body):
        if src is None:
            problems.append(f"{name!r}: delivered with no `src:` — nothing on disk to read")
            continue
        raw = _read(src)
        if raw is None:
            problems.append(f"{name!r}: src {src} "
                            f"{_unreadable(src, provisioned=True, rendered=rendered)}")
            continue
        try:
            docs.append((src.name, _grafana_provisionable_json(raw)))
        except (json.JSONDecodeError, GrafanaUnprovisionableJSON) as exc:
            problems.append(f"{src.name}: not a dashboard the provisioner loads ({exc})")
    return docs, problems


def _label_matchers(text: str, after: int) -> str | None:
    """The `{…}` matcher block a metric selector opens at `after`, or None.

    Whitespace between the name and the brace is skipped rather than read as
    "no matchers": `metric {job="x"}` is legal PromQL, and a reader that reddened
    on it would be failing a correct expression for its spacing.

    THE CLOSING BRACE IS FOUND PAST QUOTED VALUES, not by `str.find`. A matcher
    VALUE is an arbitrary string literal and may contain a `}` — `{service="a}b"}`
    is legal — so a scan that stopped at the first brace would hand
    `_promql_matchers` a truncated block. The truncated block would not parse and
    the caller would redden, which is the safe direction but for the wrong reason,
    and "the guard refuses a correct panel" is the failure this file has already
    paid for four times.
    """
    while after < len(text) and text[after].isspace():
        after += 1
    if after >= len(text) or text[after] != "{":
        return None
    i = after + 1
    while i < len(text):
        if text[i] in "\"'`":
            i = _promql_skip_quoted(text, i)
            continue
        if text[i] == "}":
            return text[after: i + 1]
        i += 1
    return text[after:]


_PROMQL_IDENT = re.compile(r"[A-Za-z_:][A-Za-z0-9_:]*")
# `re.I` BECAUSE THE PARSER FOLDS KEYWORDS, and a tokeniser that does not is
# fail-open on the commonest one-character variant of the defect it prices:
# `sum BY (code)` is legal PromQL that leaves `histogram_quantile` with zero
# samples (`logs/calibration-step04c-r3-promql-case.log` A2/B1), and a
# case-sensitive `(by|without)` does not merely misread it — it fails to pair the
# head with its own argument list, so `sum` is never returned as a call at all
# and even a fail-CLOSED unknown-head branch is never reached. An invisible
# aggregation is worse than an unclassified one.
_PROMQL_GROUPING = re.compile(r"\s*(by|without)\s*\(([^)]*)\)", re.I)

# Words that can stand in front of a `(` without being a CALL. `by`/`without` are
# read as the modifier of the call they belong to, and the set-operator and
# vector-matching keywords open a parenthesis of their own. Compared LOWER-CASED:
# every one of them folds in the parser (`AND`, `ON`, `GROUP_LEFT`, `OFFSET`,
# `BOOL` — calibration row A4).
_PROMQL_NOT_A_CALL = frozenset({
    "by", "without", "on", "ignoring", "group_left", "group_right",
    "and", "or", "unless", "offset", "bool",
})


def _promql_skip_quoted(text: str, i: int) -> int:
    """Index just past the string literal opening at `i`.

    A BACKTICK STRING IS RAW AND A BACKSLASH IN ONE IS A BACKSLASH, which is the
    same fact `_promql_unquote` implements one layer up and which this function
    contradicted for a whole round. Escape-processing all three flavours means a
    raw string ENDING in a backslash has its own closing delimiter consumed, the
    scan runs to the end of the expression, `_promql_match_paren` never pairs the
    head with its argument list, and `_promql_calls` returns NOTHING — so every
    row that iterates it says nothing about the panel.

    `sum(plex_media_count{type!=`\\`})` is the reachable case and it is not a
    parse error the engine also refuses: measured on `prom/prometheus:v3.12.0`
    over the 7/3/50 fixture, it is ACCEPTED and draws 60 against a true 10, its
    double-quoted twin `type!="\\\\"` draws the same 60, and `promql format`
    prints the two IDENTICALLY — one query, two spellings, and only the spelling
    decided whether the guard spoke (`logs/red-step04c-r8-raw-string-scanner-
    post.log` A3/A5, C3/C4; the fail-open as found, C4 of the round-7 critic's
    `logs/critic-step04c-r7-raw-string.log`). The same spelling inside a traefik
    selector hid a `sum by (code)` from the histogram row (A9/C7).

    THE OTHER TWO FLAVOURS KEEP THEIR ESCAPES, so this is a branch and not a
    simplification: `"a\\"b"` is ONE string whose escaped quote does not end it
    (B5), and the single-quoted form is the same (B6). A raw string whose
    backslash is INTERIOR was never affected (B7).

    WHAT STILL RUNS OFF THE END, on purpose: a literal with NO CLOSING DELIMITER
    at all. That is a lex error in Prometheus in every flavour — the query is
    refused and the panel ERRORS rather than drawing a plausible number (A6/A7)
    — so the invisible-call class it leads to is loud harm. See
    `_plex_media_mixed_selector` and `task-1785509072-b939`.

    THE ROWS ONLY ASK THIS ABOUT TEXT `_promql_blank_comments` HAS ALREADY
    WALKED, which is why an apostrophe in `# don't count episodes` is not a quote
    by the time a scanner gets here. `_promql_blank_comments` ITSELF IS THE
    EXCEPTION and has to be: it asks about RAW text, and that call is precisely
    what keeps a `#` inside a label VALUE the character it is (its own B4/C5). A
    sentence claiming otherwise stood here for one round and was false of the one
    caller that matters.
    """
    quote = text[i]
    i += 1
    while i < len(text):
        if text[i] == "\\" and quote != "`":
            i += 2
            continue
        if text[i] == quote:
            return i + 1
        i += 1
    return i


def _promql_blank_comments(text: str) -> str:
    """`text` with every `#` line comment replaced by SPACES, INDEX FOR INDEX.

    PROMQL HAS LINE COMMENTS AND NOTHING IN THIS FILE KNEW IT, in both
    directions. `# don't count episodes` in front of an expression opened a
    single-quoted string that never closed, so `_promql_skip_quoted` ran to the
    end, `_promql_match_paren` never paired the head with its argument list and
    `_promql_calls` returned NOTHING — measured on `prom/prometheus:v3.12.0` over
    the 7/3/50 fixture, that carrier is ACCEPTED, draws 60 against a true 10,
    `promql format` prints it IDENTICALLY to the bare `sum` (the comment carries
    no meaning at all), and the guard was PASS 17/17 on the REAL delivered
    dashboard while the same query without the comment was RED
    (`logs/red-step04c-r9-promql-comments-pre.log` A3/A4, C3; the round-8
    critic's `logs/critic-step04c-r8-promql-comment.log` B2/C2/C3). The OTHER
    direction is a false refusal: a comment INSIDE a matcher block is legal,
    normalises to the DELIVERED expression and draws the true 10 (A7), and the
    comment reached `_PROMQL_MATCHER` as an entry, so a correct panel was refused
    (C10) — as was a panel that merely NAMES a series in a comment (A11/C11).

    BLANKING, NOT SKIPPING, and the reason is the accept side. A skip branch in
    each scanner closes the fail-open and leaves the false refusal, because the
    comment is still IN the entry the matcher parser reads. Replacing it with
    spaces answers both with one clause, and index-for-index keeps every span
    this module returns — call spans, matcher blocks, `re.finditer` positions —
    valid against the caller's own string.

    THE QUOTE WALK IS FIRST, so a `#` inside a label VALUE stays the character it
    is in all three flavours (B4, and `{title="a#b"}` on the real tree, C5).
    Idempotent by construction: after one pass no `#` remains outside a string
    (B5), so applying it twice cannot change an answer.
    """
    if "#" not in text:
        return text
    out = list(text)
    i = 0
    while i < len(text):
        if text[i] in "\"'`":
            i = _promql_skip_quoted(text, i)
            continue
        if text[i] == "#":
            while i < len(text) and text[i] != "\n":
                out[i] = " "
                i += 1
            continue
        i += 1
    return "".join(out)


def _dashboard_datasource_type(node, inherited: str | None) -> str | None:
    """The datasource TYPE in force at `node`, or the inherited one.

    Only the object spelling `{"type": "prometheus", "uid": …}` states a type. The
    legacy string spelling is a datasource NAME (`"Prometheus"`) or a variable
    reference (`"$ds"`), neither of which is a type, so it leaves the answer
    inherited rather than guessed — and an unknown type is treated as prometheus
    by the row that uses this, which is the fail-closed direction.
    """
    if isinstance(node, dict):
        ds = node.get("datasource")
        if isinstance(ds, dict) and isinstance(ds.get("type"), str):
            return ds["type"]
    return inherited


def _dashboard_expr_strings(node, path: str = "$") -> list:
    """Every `expr:` string of a dashboard document, as (json path, text).

    ONE KEY, ANY DEPTH, because the depth is what varies between carriers and the
    key is what does not: a panel target is `$.panels[i].targets[j].expr`, a
    collapsed row's child target is `$.panels[i].panels[j].targets[k].expr`, and
    an annotation query is `$.annotations.list[i].expr` or, in the older
    spelling, `$.annotations.list[i].target.expr`. Enumerating those four paths
    would go blind on the fifth; keying on `expr` reaches all of them and reaches
    a nesting Grafana has not shipped yet.
    """
    out = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == GRAFANA_TARGET_EXPR_KEY and isinstance(value, str):
                out.append((f"{path}.{key}", value))
            else:
                out += _dashboard_expr_strings(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, item in enumerate(node):
            out += _dashboard_expr_strings(item, f"{path}[{i}]")
    return out


def _dashboard_variables(doc, path: str = "$") -> list:
    """Every `templating.list[]` entry a dashboard DECLARES: (json path, entry).

    ONE WALK, TWO QUESTIONS (DEC-085). `_dashboard_variable_queries` below asks
    "is this variable's own query readable"; the declared-name row asks "is every
    `$name` a panel interpolates declared at all". Both start from the same list
    and a second copy of the enumeration is a second thing to keep in step, so
    the enumeration is here and the two callers differ only in what they then ask
    of an entry.

    UNSCOPED BY `type` on purpose, unlike its caller. A `custom` variable's
    `query` is not PromQL — which is why the caller filters — but its NAME is as
    interpolable as a query variable's, so a declared-name check that inherited
    that filter would redden on `$env` the moment someone added a `custom`
    drop-down. Non-dict entries are dropped rather than reported: a
    `templating.list` holding something that is not an object is a malformed
    document, and `test_delivered_dashboards_parse_as_dashboards` owns that.
    """
    out = []
    if not isinstance(doc, dict):
        return out
    templating = doc.get("templating")
    variables = templating.get("list") if isinstance(templating, dict) else None
    if not isinstance(variables, list):
        return out
    for i, var in enumerate(variables):
        if isinstance(var, dict):
            out.append((f"{path}.templating.list[{i}]", var))
    return out


def _grafana_interpolations(text: str) -> list:
    """Every variable REFERENCE in one string, as (name, the spelling used, span).

    The name is whichever of the three alternations matched — see
    `_GRAFANA_INTERPOLATION` for where the grammar came from. The raw spelling is
    carried along for two reasons. It is what a reader has to search the file
    for, and `$guestt` / `${guestt}` / `[[guestt]]` are three different searches
    for one defect. And it is LOAD-BEARING: `_promql_capture_reference` decides
    on the text rather than the name, because the other grammar that owns `$`
    inside a dashboard string reads two of the seven texts this one forms.

    THE SPAN IS ROUND 6'S ADDITION, AND IT IS DELIBERATELY A POSITION rather than
    a second grammar's answer. Go reads the same string with a wider alphabet and
    with a `$$` escape that this tokeniser, matching at the second `$`, has no
    character left to see — so the two facts that were missing are both OUTSIDE
    the matched text, one on each side of it. Teaching this function either of
    them would make Grafana's tokeniser read two grammars at once; handing over
    where its own match sat keeps one question to one classifier and lets the
    predicate that speaks for Go do its own looking.
    """
    out = []
    for m in _GRAFANA_INTERPOLATION.finditer(text):
        name = m.group(1) or m.group(2) or m.group(4)
        if name:
            out.append((name, m.group(0), m.span()))
    return out


def _go_expand_absorbs(char: str) -> bool:
    """Would Go's `regexp.extract()` take this character INTO the name it reads?

    THE ALPHABET, TRANSCRIBED FROM THE LOOP ITSELF rather than approximated:

        i := 0
        for i < len(str) {
            rune, size := utf8.DecodeRuneInString(str[i:])
            if !unicode.IsLetter(rune) && !unicode.IsDigit(rune) && rune != '_' {
                break
            }
            i += size
        }

    `unicode.IsLetter` is category L (Lu/Ll/Lt/Lm/Lo); `unicode.IsDigit` is
    category Nd — NOT Nl, NOT No. Python's `str.isalpha()` is exactly L and
    `str.isdecimal()` is exactly Nd, so these three tests are those three tests,
    clause for clause. Python's own `\\w` is NOT the same predicate: it takes
    `isalnum()`, which swallows Nl and No, and a `\\w`-shaped boundary would
    refuse `$ctⅧ` and `$ct²` — two references the pinned engine really does
    expand, to `110Ⅷ` and `110²`. An `re.ASCII`-shaped one would refuse `$ctµ`,
    whose `µ` is an ordinary Ll. Both wrong directions are measured rather than
    argued, per category and on both halves of Go's grammar, in
    `logs/calibration-step05a-r6-name-boundary.py`.

    WHAT THIS DOES NOT PIN, said rather than left to be found: the calibration
    puts sixteen characters to the engine — L's five subcategories, Nd in two
    scripts, and the No/Nl/Mn/Pd near-misses that decide the rule — so it pins
    the RULE and not every codepoint. A Unicode-database skew between this
    interpreter and the pinned Go build could still disagree about a character
    assigned in one and not the other. That is a claim about the two libraries'
    UCD versions and nothing else; it is not a claim that no such character
    exists.

    The empty string — nothing follows, the reference ends the JSON string — is
    absorbed by no clause, which is the common case and the correct answer.
    """
    return char.isalpha() or char.isdecimal() or char == "_"


def _grafana_substituted_spans(text: str, substituted: set) -> list:
    """Where in this string Grafana REPLACES the bytes before Go reads any of them.

    THE TWO GRAMMARS DO NOT SHARE A TEXT — they share it IN SEQUENCE, and only
    the second half of that sequence is Go's. `templateSrv.replace()` runs first,
    in ONE global `String.replace` pass, and hands Prometheus its OUTPUT: a
    DECLARED name (or a built-in, which `updateIndex` writes into the same
    variable index) has become its VALUE by then, while an undeclared one takes
    the `return match` branch and survives as its own text. So the spans this
    returns are exactly the places where the on-disk bytes are NOT the bytes Go
    receives, and everything else in the string is passed through unchanged.
    Sourced clause by clause in `logs/calibration-step05a-r7-substitution-boundary.py`
    (G1-G3).

    `substituted` is `declared | GRAFANA_BUILT_IN_VARIABLES` and is deliberately
    a SUPERSET of what is really replaced — `timeFilter` is in Grafana's own
    global list without being a macro or an index entry (G4). A superset can only
    make a caller REFUSE an exemption, never grant one, which is the direction
    this file is allowed to be wrong in.
    """
    return [span for name, _spelling, span in _grafana_interpolations(text)
            if name in substituted]


def _promql_capture_reference(text: str, span: tuple, groups: set,
                              substituted: set) -> bool:
    """Is this undeclared reference a Go capture group rather than a variable?

    IT TAKES THE STRING, WHERE IN IT, AND WHICH NAMES GRAFANA WILL REPLACE,
    because Go's `Expand` does not take this string — it takes
    `templateSrv.replace()`'s OUTPUT, and the three arguments together are what
    says which bytes of this one survive into that one. Round 4 was handed the
    NAME and exempted five dead texts per working one. Round 5 was handed the
    TEXT and fixed that, but an anchored pattern sees only inside the match.
    Round 6 added the character on each side of the match and claimed the on-disk
    string was what Expand takes; it is not, and BOTH of those characters can be
    supplied by a neighbouring substitution instead of by the file.

    FOUR FACTS, ALL MEASURED, IN THE ORDER GO ASKS THEM:

    1. IS THIS `$` A REFERENCE AT ALL, or the second half of a `$$` escape? Go
       consumes `$$` as a literal `$` before it ever calls `extract()`, so the
       parity of the `$` run in front of the match decides — even, and this is a
       reference; odd, and Go already spent it. `$$ct` draws the literal text
       `$ct`; `$$$ct` draws `$110`. AND THAT RUN IS ONLY THIS FILE'S WHEN NO
       SUBSTITUTION ENDS AT THE RUN'S FAR EDGE — `start - run`, which is the
       match itself only when the run is empty. GO PAIRS FROM THE START OF A
       MAXIMAL RUN, so what decides the parity is the whole run in the text Go
       receives, and a value ending in `$` lengthens it from the far side however
       many `$` this file wrote: `$guest$$$ct` (run=2) is a reference for an
       ordinary value (three `$`, `lxc/110$110`) and LITERAL TEXT for a
       `$`-terminated one (four, `lxc/110$$ct`) — same bytes on disk, opposite
       answers — and `$guest$$$$$ct` (run=4) is the same fact one run further
       out, five `$` drawing `lxc/110$$110` against six drawing `lxc/110$$$ct`,
       which is why the test is the RUN and not the number two. The value is
       unknowable here, so that case is refused, on BOTH spellings, because
       pairing is decided in front of the `$` and a brace cannot reach there
       (E2/E3/E5 of `logs/critic-step05a-r7-parity-run-seam.log` at run=2,
       E1/E2 of round 8's calibration at run=4).
       It is a DISTANCE and not a ban: one separator puts the neighbour off the
       far edge and `$guest-$$$ct` then works for every value (E5), which is also
       why `$$$ct` with nothing in front keeps its exemption.

       THE RIGHT-HAND END HAS NO DISTANCE ANALOGUE and fact 3 is written at zero
       deliberately: Go's name ends at the first character `extract()` does not
       absorb, so if `text[end]` is not absorbed nothing beyond it can extend the
       name, and if it is absorbed this predicate has already refused.
    2. IS THE TEXT ONE GO READS AT ALL — `$name` or `${name}`, and nothing else
       of the seven Grafana forms (`_PROMQL_EXPAND_REFERENCE`).
    3. DOES GO'S NAME END WHERE GRAFANA'S DID? Only the unbraced spelling can
       disagree: `${ct}` is closed by a `}` that both readers stop at, while
       `$ct` runs on into whatever follows. TWO THINGS CAN FOLLOW IT. A character
       of this file, if Go's `extract()` would absorb it (`_go_expand_absorbs`) —
       `$ctß` is a reference to `ctß`, and the exemption must not answer for it
       with `ct`. Or a SUBSTITUTED value, if a replaced reference begins exactly
       where this match ended: `$ct$guest` reaches Go as `$ctlxc/110`, the name
       `ctlxc` resolves to empty and the leftover literal stays, so the label
       comes out `"/110"` — wrong rather than missing (E2). Again the value is
       unknowable, so it is refused; and again the scope is exact, because
       `${ct}$guest` really is a working query (E4) and stays exempt.
    4. IS THAT NAME a group by POSITION (`_PROMQL_CAPTURE_GROUP`) or one the SAME
       STRING declares by name (`_PROMQL_GROUP_DECLARATION`)?

    The caller has already established that the reference is not a declared
    Grafana variable, which is the order that matters: a declaration always wins,
    so a dashboard that really declares `1` or `ct` is answered by this row
    rather than skipped by it.

    WHAT THE TWO ABUTMENT CLAUSES COST, PRICED RATHER THAN ASSUMED FREE. On the
    right they cost nothing: every value whose first character Go absorbs breaks
    the query, and `$ct$guest` is the string this repair exists for. On the LEFT
    they cost a real query — `$guest$ct` works for every value that does not end
    in `$` (E7), and it is refused anyway, because the one that does end in `$`
    is silent. BOTH REFUSALS HAVE THE SAME ONE-CHARACTER ESCAPE, which is why
    fail-closed is affordable here: a separator restores both ends (`$ct-$guest`
    → `110-lxc/110`, `$guest-$ct` → `lxc/110-110`, E6/E11), and on the right the
    brace form does too. The refusal is not silent either — the row below names
    the file, the json path and the string.

    AND THE CLAUSES ARE ABOUT SUBSTITUTION, NOT ADJACENCY. An undeclared
    neighbour is left literal by Grafana, so it changes nothing Go reads and this
    predicate still exempts: `$ct$guestt` keeps its skip while `guestt` itself is
    reported by the caller. That row is the one that locates the repair — a rule
    written on "is there another interpolation next to it" would print `0
    skipped` there.

    THE MEMBERSHIP TEST IS EXACT, and round 5's was exact over the wrong name —
    Grafana's. Go takes a name as long as possible, so `$ctx` beside `(?P<ct>…)`
    is a reference to `ctx` and expands to empty (an exact test agrees with the
    engine where a prefix test would not); fact 3 is the same sentence where the
    two alphabets differ rather than the two names.
    """
    start, end = span
    replaced = _grafana_substituted_spans(text, substituted)
    before = text[:start]
    run = len(before) - len(before.rstrip("$"))
    if run % 2:
        return False
    if any(stop == start - run for _begin, stop in replaced):
        return False
    m = _PROMQL_EXPAND_REFERENCE.match(text[start:end])
    if m is None:
        return False
    if m.group(1) and (_go_expand_absorbs(text[end:end + 1])
                       or any(begin == end for begin, _stop in replaced)):
        return False
    name = m.group(1) or m.group(2)
    return bool(_PROMQL_CAPTURE_GROUP.match(name)) or name in groups


def _promql_group_declarations(text: str) -> set:
    """Every regex capture-group NAME one string declares, in either Go spelling."""
    return {m.group(1) for m in _PROMQL_GROUP_DECLARATION.finditer(text)}


def _grafana_axis_double(value) -> float | None:
    """One axis as the DOUBLE the comparator holds, or None if it is not a place.

    THE TEST IS "IS THIS A JSON NUMBER", NOT "CAN JAVASCRIPT SUBTRACT IT" — see
    `GRAFANA_PANEL_POSITION_KEY` for the two operators and the measurement. A
    Python `bool` IS an `int`, and it is the member of the coercing class that
    opens the ACCEPT side (`true` reads as 1 here and as "equal to 1, ordered
    against everything else" there), so it is tested FIRST and by `isinstance`:
    `value in (True, False)` would take 1 and 0 with it (r7 C6).

    A NON-FINITE VALUE CANNOT REACH THIS FROM A DELIVERED FILE, AND IT IS STILL NOT A
    PLACE. Round 7 read a `NaN` token as unreadable and an `Infinity` token as the
    ordinary float `inf`, and converted an int past the double range into an infinity
    "because that is what `JSON.parse` gives it" — but no browser ever sees such a
    file: `_grafana_provisionable_json` refuses it at the parse, where the provisioner
    does (r8 A2-A6). The clause stays because this function is also called directly,
    and it now says the same thing the loader does rather than something narrower on
    one token and wider on the next.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        number = float(value)
    except OverflowError:
        return None                      # an int past the double range: no file carries one
    if number != number or number in (float("inf"), float("-inf")):
        return None                      # not a finite double, so not an order
    return number


def _grafana_panel_position(entry) -> tuple | None:
    """One `panels[]` entry's sort key `(y, x)`, or None if it does not have one.

    ABSENT IS (0, 0) AND EVERYTHING ELSE THE FILE WRITES IS ITSELF — see
    `GRAFANA_PANEL_POSITION_KEY` for every half of that measured out of the pinned
    image. `defaultsDeep` fills every axis the file OMITS, down to a partial
    `gridPos`, and an entry that is not an object at all is a `PanelModel` with
    nothing to keep, so those are the origin. A `gridPos` the file DID write is
    kept as written, so a null one is not the origin — it is a comparator that
    throws — and a value that is not a JSON number is not a position, whether it
    reaches the comparator as NaN or as a number `===` disowns.
    """
    if not isinstance(entry, dict) or GRAFANA_PANEL_POSITION_KEY not in entry:
        return (float(GRAFANA_PANEL_POSITION_DEFAULT),) * len(GRAFANA_PANEL_POSITION_AXES)
    grid = entry[GRAFANA_PANEL_POSITION_KEY]
    if not isinstance(grid, dict):
        return None
    key = []
    for axis in GRAFANA_PANEL_POSITION_AXES:
        value = _grafana_axis_double(grid.get(axis, GRAFANA_PANEL_POSITION_DEFAULT))
        if value is None:
            return None
        key.append(value)
    return tuple(key)


def _grafana_panel_order(panels: list, path: str) -> tuple | None:
    """The order Grafana walks this list in, as ORIGINAL indices — None if unreadable.

    `sorted` is stable and so is `Array.prototype.sort`, which is what makes this
    inert on every file whose array order already is its `gridPos` order — the
    delivered dashboard, and anything Grafana itself saved.
    """
    if path != GRAFANA_SORTED_PANEL_LIST_PATH:
        return tuple(range(len(panels)))
    keys = [_grafana_panel_position(entry) for entry in panels]
    if any(key is None for key in keys):
        return None
    return tuple(sorted(range(len(panels)), key=keys.__getitem__))


def _grafana_row_span(panels: list, i: int, path: str) -> tuple:
    """The json paths an EXPANDED repeating row at `panels[i]` owns as CHILDREN.

    A ROW IS THE ONE ENTRY WHOSE CHILDREN ARE NOT UNDER IT, and only in one of its
    two spellings — see `GRAFANA_ROW_PANEL_TYPE` for the four links that decide
    this. An expanded row (`Boolean(collapsed)` false) collects the entries that
    FOLLOW it in the same list up to the next row; a collapsed one carries its
    children nested, where the caller's own path prefix already reaches them, and
    its siblings belong to nobody.

    AND "FOLLOW" IS IN GRAFANA'S ORDER, WHICH IS THE SCREEN'S AND NOT THE FILE'S —
    `GRAFANA_PANEL_POSITION_KEY`, and round 5's fifth unstated bound. The walk is
    over `_grafana_panel_order`: `(gridPos.y, gridPos.x)` for the dashboard's own
    `panels[]`, file order for a collapsed row's nested list, which is the only
    other list this is asked of. A row written first and positioned last owns
    NOTHING, a row appended last and positioned first owns everything, and the
    json paths emitted are the ORIGINAL indices either way, so the carrier stays
    the place the file really writes it.

    THE SPAN IS RETURNED BESIDE THAT PREFIX RATHER THAN INSTEAD OF IT, so the
    clause keeps ONE carrier path — the place the `repeat` is actually written,
    which is what the declared-name row prints — and the coverage stays a set of
    prefixes `_panel_repeats_over` tests exactly as before.

    THE STOP CONDITION IS `type: "row"` AND NOT "a repeat clause": Grafana commits
    the previous row's panels on `currentRow.id !== panel.id` for ANY next row,
    repeating or not, collapsed or not, so a second row ends the span whatever it
    says. Asked only of a row, never of an ordinary panel — `repeat` on a `stat`
    repeats that panel and touches no sibling (round 4's E4, this round's B7).

    AN UNREADABLE POSITION ANYWHERE IN THE LIST WITHHOLDS THE WHOLE SPAN, not just
    that entry's place in it: one key the comparator does not order moves the row
    relative to everything else, so no part of the answer survives it. That is a
    false refusal of a dashboard that may well render, and it is the priced
    direction — the row names the file and the path, and a number puts the
    exemption back (r6 C5/C6, r7 B2/B3/B4).

    AND "UNREADABLE" IS WIDER THAN "NaN", which is the bound round 6 stated and
    round 7 measured: `true`, `false`, `null`, `""` and `[]` are all subtractable
    and none of them is `===` to the number they subtract to, so each is ordered
    like that number and never tied with it — a place in one list and not in the
    next. `_grafana_axis_double` refuses the whole class, and
    `GRAFANA_PANEL_POSITION_KEY` carries the measurement and the two prices.
    """
    row = panels[i]
    if row.get("type") != GRAFANA_ROW_PANEL_TYPE:
        return ()
    if row.get(GRAFANA_ROW_COLLAPSED_KEY) not in GRAFANA_FALSY_VALUES:
        return ()
    order = _grafana_panel_order(panels, path)
    if order is None:
        return ()
    span = []
    for j in order[order.index(i) + 1:]:
        entry = panels[j]
        if isinstance(entry, dict) and entry.get("type") == GRAFANA_ROW_PANEL_TYPE:
            break
        span.append(f"{path}.panels[{j}]")
    return tuple(span)


def _dashboard_repeat_clauses(node, path: str = "$") -> list:
    """Every `repeat` clause of a dashboard, as (json path, BARE name, paths COVERED).

    THE CARRIER `_grafana_interpolations` CANNOT SEE, because it is the one place
    the save model names a variable without a sigil — see
    `GRAFANA_BARE_VARIABLE_KEY` for where that is read from. `"repeat": "guest"`
    is a reference to the variable `guest`; there is no `$` for a tokeniser to
    find, so a rename that fixes all thirteen `$guest` and leaves the repeat
    clause behind is invisible to every other reader in this file, and the panel
    simply stops repeating.

    SCOPED TO `panels[]` ENTRIES rather than keyed at any depth, which is the
    opposite of `_dashboard_expr_strings`' argument and for the opposite reason.
    `expr` is a word only a query carrier uses, so keying on it reaches a nesting
    Grafana has not shipped yet at no cost. `repeat` is an ordinary English word
    that any panel plugin's options may spell, and reading one as a variable name
    would be a false refusal. The schema says where it lives — `repeat?: string`
    is declared on Panel and on RowPanel, both of which are `panels[]` entries —
    so this walks `panels[]` at any depth, which reaches a collapsed row's
    children (`$.panels[i].panels[j]`) without guessing about anything else.

    An empty or non-string clause is not a reference and is dropped: Grafana's
    `if (row.repeat)` / `panel.repeat ? … : undefined` say the same.

    THE THIRD MEMBER IS WHAT THE CLAUSE COVERS, and it is a walk's answer rather
    than a reader's because it needs the SIBLINGS: an expanded row's children are
    the entries beside it in this very list (`_grafana_row_span`), and no consumer
    holding one clause could work that out. Its own carrier path is always in the
    set, so a panel's repeat covers its own subtree exactly as it did before, and
    a collapsed row's nested children are still reached by that prefix.
    """
    out = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "panels" and isinstance(value, list):
                for i, panel in enumerate(value):
                    if isinstance(panel, dict):
                        name = panel.get(GRAFANA_BARE_VARIABLE_KEY)
                        if isinstance(name, str) and name:
                            at = f"{path}.panels[{i}]"
                            out.append((f"{at}.{GRAFANA_BARE_VARIABLE_KEY}", name,
                                        (at,) + _grafana_row_span(value, i, path)))
                    out += _dashboard_repeat_clauses(panel, f"{path}.panels[{i}]")
                continue
            out += _dashboard_repeat_clauses(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, item in enumerate(node):
            out += _dashboard_repeat_clauses(item, f"{path}[{i}]")
    return out


def _dashboard_variable_queries(doc, path: str = "$") -> list:
    """A template variable's QUERY, as (json path, text) — its prose left alone.

    `definition` and `query` are the two the Prometheus variable editor writes,
    the second either as a string (legacy) or as `{"query": …, "refId": …}` (the
    delivered `pve` dashboard's spelling). A variable also carries a `label`, a
    `description` and its resolved `options`, and none of those is a query.

    SCOPED BY `type`, because `query` is not always one: see
    `GRAFANA_NON_QUERY_VARIABLE_TYPES`. A variable whose type is neither
    `query` nor one of those is not read here AND is reported by
    `test_delivered_dashboard_queries_are_readable`, so an unknown type is a
    refusal rather than a silent skip.

    The `templating.list[]` enumeration itself is `_dashboard_variables`, shared
    with the declared-name row so the two questions cannot drift apart.
    """
    out = []
    for base, var in _dashboard_variables(doc, path):
        if var.get("type") != GRAFANA_QUERY_VARIABLE_TYPE:
            continue
        for key in GRAFANA_VARIABLE_QUERY_KEYS:
            value = var.get(key)
            where = f"{base}.{key}"
            if isinstance(value, str):
                out.append((where, value))
            elif isinstance(value, dict) and isinstance(value.get("query"), str):
                out.append((f"{where}.query", value["query"]))
    return out


def _dashboard_query_strings(doc, path: str = "$") -> list:
    """Every string a dashboard DECLARES as a query, as (json path, text)."""
    return _dashboard_expr_strings(doc, path) + _dashboard_variable_queries(doc, path)


def _dashboard_query_carriers(node, path: str = "$", inherited: str | None = None) -> list:
    """Every PLACE a dashboard declares a query: (json path, kind, node, ds type).

    The dual of `_dashboard_query_strings` — that one returns the queries this
    file can READ, this one returns the slots a query lives in whether or not a
    readable one is in them, so the difference between the two can be reported
    instead of skipped. Kinds: a `targets[]` entry, an `annotations.list[]`
    entry, a `templating.list[]` variable.
    """
    out = []
    if isinstance(node, dict):
        here = _dashboard_datasource_type(node, inherited)
        for key, value in node.items():
            if key == "targets" and isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        out.append((f"{path}.targets[{i}]", "target", item,
                                    _dashboard_datasource_type(item, here)))
                continue
            if key == "annotations" and isinstance(value, dict) \
                    and isinstance(value.get("list"), list):
                for i, item in enumerate(value["list"]):
                    if isinstance(item, dict):
                        out.append((f"{path}.annotations.list[{i}]", "annotation", item,
                                    _dashboard_datasource_type(item, here)))
                continue
            if key == "templating" and isinstance(value, dict) \
                    and isinstance(value.get("list"), list):
                for i, item in enumerate(value["list"]):
                    if isinstance(item, dict):
                        out.append((f"{path}.templating.list[{i}]", "variable", item,
                                    _dashboard_datasource_type(item, here)))
                continue
            out += _dashboard_query_carriers(value, f"{path}.{key}", here)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            out += _dashboard_query_carriers(item, f"{path}[{i}]", inherited)
    return out


def _promql_strings(doc, path: str = "$") -> list:
    """Every string a dashboard DECLARES AS A QUERY, comments blanked.

    A DESCRIPTION IS PROSE BESIDE THE QUERY, NOT A QUERY, and until round 11 this
    returned `_json_strings` — every string LEAF the JSON carries — so the three
    rows below read a panel's `description`, `title` and `legendFormat` as
    expressions and reddened the most ordinary authoring act there is. Measured on
    the REAL dashboard (`logs/red-step04c-r11-prose-not-expression-pre.log`
    C2-C5): a description documenting the latency panel's own series is 15/17,
    printing "carries NO label matcher — that series exists once per service, so
    this panel graphs the whole proxy under a Plex title" AND "reads … outside
    histogram_quantile()" about a SENTENCE, while every `expr` of that panel is
    byte-identical and the engine draws the correctly-scoped 0.91 (A1; the
    whole-proxy spelling really does draw a different number, A2 — the sentence is
    meaningful, just false of the prose). A `legendFormat` is 15/17, a `title`
    15/17, and a library description QUOTING the expression an author must NOT
    write is 16/17 with the prose COUNTED as an aggregation.

    AND THE ASYMMETRY IS WHAT SHOWED IT WAS NOT A DECLARED PRICE: naming the PLEX
    series in prose was GREEN throughout, because the `plex_*` name row accepts a
    DECLARED series anywhere, so the rule the file actually enforced was "you may
    document the plex metric and not the traefik one", which nobody wrote down.

    SO THE TWO QUESTIONS ARE SEPARATED AT THE READER. "Does any string NAME a
    series that does not exist" wants every string, and
    `test_plex_panels_name_series_the_exporter_declares` and its `pve_*` twin
    KEEP `_json_strings` for exactly that — breadth is their point, a near-miss in
    a title is still a panel that will never populate. "Does this EXPRESSION
    select what it claims" wants the fields where a dashboard DECLARES an
    expression, which is `_dashboard_query_strings`. Those fields, spelled as the
    paths they are: `$.panels[i].targets[j].expr` and the same key at any other
    depth — `$.panels[i].panels[j].targets[k].expr` inside a collapsed row,
    `$.annotations.list[i].expr` and `$.annotations.list[i].target.expr` — plus a
    `query` variable's `$.templating.list[i].definition`,
    `$.templating.list[i].query` and `$.templating.list[i].query.query`. The first
    three of those and the last two are the ones the two delivered dashboards
    actually use; the rest are Grafana's schema, not a guess.

    THE NARROWING IS ONLY HONEST BECAUSE WHAT IT STOPS READING IS REPORTED.
    `test_delivered_dashboard_queries_are_readable` reddens on a prometheus
    target, annotation or query variable whose query is NOT in one of those
    fields, so the next key Grafana invents arrives as a refusal naming the keys
    it did find — not as three rows quietly finding nothing to check. That row is
    also this file's anti-vacuity for the reader itself: zero readable queries
    across the delivered dashboards FAILS.

    ONE BLANKING SITE, AND IT IS HERE BECAUSE THE SCANNERS ARE NOT THE ONLY
    READERS. The three rows below also ask their question of the raw text
    (`"histogram_quantile(" not in text`, `re.search(r"\\b(rate|irate|increase)"`,
    `subject.search(text, start, end)`), and every one of those was satisfied by a
    MENTION in a comment: measured, `# TODO: wrap the ladder in rate()` in front
    of a quantile over RAW cumulative counters was GREEN 17/17 while the engine
    drew it (`logs/red-step04c-r9-promql-comments-pre.log` A9/C12), and
    `# the histogram_quantile() belongs in a recording rule` in front of a bare
    bucket sum likewise (A10/C13). Blanking inside the scanners alone would have
    closed the half the review named and left these; taking the text through one
    funnel closes the class.

    WHY THE SCANNERS DO NOT BLANK AGAIN, since blanking is idempotent and a
    second call would be free. Every path into `_promql_calls`, `_label_matchers`,
    `_promql_matchers`, `_promql_subject_reaches` and
    `_plex_media_mixed_selector` starts at a row, and every row that reads an
    expression reads it from here — exactly ONE loop in this file still iterates
    the unblanked strings, and it is the NAME row's (measured,
    `logs/red-step04c-r9-promql-comments-post.log` B12,
    `logs/red-step04c-r11-prose-not-expression-post.log` F5). A second blanking
    would therefore be a branch no
    caller can reach, and "a refusal nobody asks for reads like coverage" is this
    file's own sentence about exactly that. The scanners say what they require in
    their docstrings instead; what decides is the end-to-end rows on the REAL
    dashboard (PART C), not a helper asked in isolation.
    """
    return [(where, _promql_blank_comments(text))
            for where, text in _dashboard_query_strings(doc, path)]


def _promql_match_paren(text: str, opened: int) -> int | None:
    """Index of the `)` closing the `(` at `opened`, or None if unbalanced."""
    depth = 0
    i = opened
    while i < len(text):
        ch = text[i]
        if ch in "\"'`":
            i = _promql_skip_quoted(text, i)
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def _promql_calls(text: str) -> list:
    """Every `head(…)` call in an expression, with its grouping modifier.

    Returns `(head, clause, labels, arg_start, arg_end)` per call — `clause` is
    `"by"`, `"without"` or None, `labels` the raw text inside the modifier's
    parentheses, and `arg_start`/`arg_end` the span of the call's own argument
    list. The two checks below ask "which calls are applied to THIS series", and
    that is a question about a SPAN, so the span is what this returns.

    BOTH SPELLINGS OF THE MODIFIER ARE READ, leading and trailing, because they
    are the same expression: the real parser normalises `sum(foo) by (le)` to
    `sum by (le) (foo)` (`logs/calibration-step04c-r2-promql-aggregation.log`
    row A3). A reader that saw only the leading spelling would reject a correct
    panel, which is the other half of the same failure as accepting a broken one.

    THE CLAUSE COMES BACK LOWER-CASED AND THE LABELS DO NOT. `BY`/`WITHOUT` are
    keywords and fold; a LABEL NAME is not a keyword and does not — `by (LE)`
    groups by a label the bucket series has never carried, so it collapses `le`
    exactly like `by (code)` does (calibration A5, engine B12/B13). Folding the
    label set as well would make the guard accept that.

    Quoted strings are skipped rather than scanned, so a parenthesis or a
    keyword inside a label value or a `count_values` name is not read as syntax.
    A `#` COMMENT is not read as syntax either, and that is not this function's
    doing: it is blanked to spaces once, at `_promql_strings`, before any row
    hands text to any scanner here.

    THE DECLARED GAP, MEASURED AND LEFT OPEN ON PURPOSE: an UNTERMINATED string
    literal swallows the rest of the expression, so `_promql_match_paren` never
    pairs the head with its argument list and this returns NO call at all —
    `sum(plex_media_count{"type!="show_episode"})` comes back `[]` while its
    balanced twin comes back with one `sum`. Every row that iterates this function
    therefore says nothing about such an expression. That is the invisible-
    construct shape of `mem-1785501296-8c6b` one layer up, and it is priced as the
    LOUD class rather than fixed: an unterminated literal is a lex error in
    Prometheus (`logs/calibration-step04c-r5-matchers.log` A8), so the expression
    never returns a sample and the panel shows an ERROR instead of a plausible
    wrong number — which is exactly what Step 4d's operator is looking at, and the
    opposite of the "populates and is always wrong" class these rows exist for.
    The cheap fix — refusing any subject whose `{…}` block does not parse, calls or
    no calls — would redden `plex_media_count{$filter}`, the ordinary Grafana idiom
    of interpolating a matcher list from a template variable, and trading a new
    false refusal of a real authoring shape for a hole whose harm is visible is the
    wrong way round. Filed as `code-assist:plex-monitoring:guard:promql-
    unterminated-string`; see DEC-090 and battery row R21'.
    """
    calls = []
    i, n = 0, len(text)
    while i < n:
        if text[i] in "\"'`":
            i = _promql_skip_quoted(text, i)
            continue
        ident = _PROMQL_IDENT.match(text, i)
        if not ident:
            i += 1
            continue
        head = ident.group(0)
        i = ident.end()
        if head.lower() in _PROMQL_NOT_A_CALL:
            continue
        leading = _PROMQL_GROUPING.match(text, i)
        j = leading.end() if leading else i
        while j < n and text[j].isspace():
            j += 1
        if j >= n or text[j] != "(":
            continue
        end = _promql_match_paren(text, j)
        if end is None:
            continue
        modifier = leading or (None if leading else _PROMQL_GROUPING.match(text, end + 1))
        calls.append((head, modifier.group(1).lower() if modifier else None,
                      modifier.group(2) if modifier else None, j, end))
    return calls


def _promql_label_set(labels: str | None) -> set:
    """The label NAMES a grouping clause holds, as the parser reads them.

    A LABEL NAME MAY BE QUOTED AND THE QUOTES ARE NOT PART OF THE NAME. PromQL
    3.x accepts `sum without ("le") (…)` and normalises it to `sum without (le)
    (…)` — all three quote flavours, in both modifier positions, and for each
    name of a multi-name clause (`logs/calibration-step04c-r4-promql-quotes-and-
    selection.log` A1/A2, read off `promql format`, i.e. the parser's own AST).
    Stripping whitespace ONLY, as this did, is the round-3 defect one token class
    over, and in both directions: `sum without ("le")` was GREEN here while the
    engine returned ZERO samples for the quantile above it (B1), the library
    panel's `without ("title", "type")` was GREEN at 60 against a true 10 (B4),
    and the CORRECT `sum by ("le")` (engine: the interpolated p90, B3) was RED.

    A BALANCED PAIR, NOT A STRIP. `name.strip("\\"'`")` would also turn the
    unbalanced `"le` into `le` — and `sum by ("le` does not parse at all (A6), so
    calling that panel correct would be an accept the engine never gives. An
    unbalanced quote therefore stays in the name, matches nothing, and reddens.

    UNQUOTE, NEVER FOLD. Quoting does not change a label name's CASE: `by ("LE")`
    comes back out of the parser as `LE` (A3), which no bucket series carries, so
    it collapses `le` exactly like `by (code)` does. And a quoted name that is not
    a bare identifier — `by ("le.x")` — is a legal, DIFFERENT label (A5). Both
    stay RED, which is what keeps this an unquote and not a normalisation.
    """
    names = set()
    for name in (labels or "").split(","):
        name = name.strip()
        if len(name) >= 2 and name[0] in "\"'`" and name[-1] == name[0]:
            name = name[1:-1]
        names.add(name)
    return names


# A PromQL STRING LITERAL, all three flavours. The double- and single-quoted
# forms take Go escapes; the backtick form is raw and takes none (measured, all
# three, `logs/calibration-step04c-r5-matchers.log` A1/A2/A3 — each normalises to
# the same AST).
_PROMQL_STRING = r"\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|`[^`]*`"
# ONE LABEL MATCHER, ANCHORED AT BOTH ENDS OF ITS OWN ENTRY. `\Z` is the whole
# point: the reader this replaced asked `'type!="show_episode"' in <the block>`,
# and `{mediatype!="show_episode"}` contains that substring, so a one-word typo
# was GREEN while the engine returned the row's own 60 against a true 10
# (calibration B14). A name is matched as a NAME or not at all.
_PROMQL_MATCHER = re.compile(
    rf"\s*(?P<name>{_PROMQL_STRING}|[A-Za-z_][A-Za-z0-9_]*)"
    rf"\s*(?P<op>=~|!~|!=|=)"
    rf"\s*(?P<value>{_PROMQL_STRING})\s*\Z")
# THE TWO OPERATORS THAT READ THEIR VALUE AS A PATTERN, named because one caller
# asks the literal-vs-regex question rather than the positive-vs-negative one. The
# split is NOT `=` versus the rest: `!~` against `(lxc/110|lxc/111)` returns
# exactly the series neither container owns, while `!=` against the same string
# returns EVERY series including both containers, because no id equals that text
# (`logs/calibration-step05d-rework-r3-includeall.py` C2/C3/C4). Membership is
# tested rather than complemented so an operator this file learns to parse later
# is treated as a literal one — the refusing direction, loud, and the direction
# every unknown in this file already pays.
PROMQL_REGEX_OPERATORS = frozenset({"=~", "!~"})
# The label the metric name IS. PromQL 3.x lets a selector carry its name inside
# the block, either as this label or as a bare string entry the parser normalises
# to it, and both spellings select exactly what the name-in-front spelling does
# (`logs/calibration-step04c-r10-name-in-braces-grammar.log` A3/A4).
PROMQL_NAME_LABEL = "__name__"
# THE LEXER'S ESCAPE GRAMMAR, all of it. Prometheus' `lexEscape` is Go's string
# syntax: this simple set plus the OPENING quote, then four NUMERIC families, then
# a range check. Everything else is a lex error. Measured row by row against
# `prom/prometheus:v3.12.0` in `logs/calibration-step04c-r7-lexer-escapes.log`
# (46/46) — see `_promql_unquote` for why a table with only the simple half was a
# silent fail-open and not merely an incompleteness.
_PROMQL_SIMPLE_ESCAPES = {"\\": "\\", "a": "\a", "b": "\b", "f": "\f", "n": "\n",
                          "r": "\r", "t": "\t", "v": "\v"}
# escape -> (digits, base, the largest value it may denote)
_PROMQL_NUMERIC_ESCAPES = {"x": (2, 16, 0xFF), "u": (4, 16, 0x10FFFF),
                           "U": (8, 16, 0x10FFFF)}
_PROMQL_OCTAL_DIGITS = "01234567"
_PROMQL_HEX_DIGITS = "0123456789abcdefABCDEF"
# A POSIX BRACKET EXPRESSION — the ONE syntax class RE2 and this gate's `re` both
# COMPILE and read differently. RE2 (Go's `regexp`, which is what Prometheus
# compiles a label regex with) supports `[:alpha:]` and its negated form
# `[:^digit:]` INSIDE a bracket expression; Python's `re` has never supported
# them, reads `[[:alpha:]]` as the literal set `{[ : a l p h }` and says only
# `FutureWarning: Possible nested set`. See `_promql_regex_matches` for the full
# enumeration and for why every OTHER divergence is loud.
#
# NOT ANCHORED ON `[[:`, which is only the commonest spelling. The class is a
# member of a bracket expression like any other, so `[a-z[:punct:]]+` is the same
# construct and diverges the same way (calibration A8) — the near-miss a detector
# written against the example in the review would not see.
_PROMQL_POSIX_CLASS = re.compile(r"\[:\^?[a-zA-Z]+:\]")


def _promql_unquote(token: str) -> str | None:
    """The text a PromQL string literal denotes, or None if it is not one.

    A BALANCED PAIR, THE SAME RULE `_promql_label_set` PAYS FOR. An unbalanced
    quote is not a string, and `{"type!="show_episode"}` — which is exactly what a
    dropped quote looks like — does not parse at all (r5 calibration A8). Returning
    None makes its caller refuse the block instead of reading a name out of it.

    A DECODER MUST IMPLEMENT THE ESCAPES THE LEXER ACCEPTS, NOT ONLY THE ONES IT
    REJECTS, and the difference was a silent fail-open at this row's own number.
    The table here used to be the simple set alone, with every other escape left
    as the two characters it was written as, on the argument that "Go rejects the
    expression outright anyway". That argument is false for four families:
    `lexEscape` takes `\\xNN`, `\\NNN` octal, `\\uNNNN` and `\\UNNNNNNNN` exactly as
    Go string syntax does. So `type=~"[[\\x3aalpha\\x3a]_]+"` reached RE2 as
    `[[:alpha:]_]+` and drew 60 against a true 10, while this function handed
    Python a string with no `[:` in it at all, `_PROMQL_POSIX_CLASS` found
    nothing, and the selector was called a one-kind pin — never empty, always
    wrong, and ticked by Step 4d's operator. All four spellings, the octal and
    both unicode widths included, are measured at that same 60
    (`logs/calibration-step04c-r7-lexer-escapes.log` A1-A4, E1-E4).

    THE DIRECTION WAS ASYMMETRIC, WHICH IS WHY ONLY HALF OF IT WAS EVER VISIBLE.
    On the two EQUALITY readers a mis-decode makes the value COMPARE UNEQUAL, so
    `service="plex\\x40file"` — which the engine resolves to the delivered latency
    panel's own series (F1) — and `type!="show\\x5fepisode"` (F2, engine 10, the
    delivered library expression) were LOUD false refusals of correct panels. The
    fail-open needs the REGEX branch, where a mangled pattern still compiles.
    Decoding is what fixes both directions at once; refusing every escape this
    table did not know would have fixed the silent half by charging a false
    refusal of legal PromQL, in a file already rejected twice for forbidding the
    real answer.

    AND WHAT THE LEXER REFUSES, THIS REFUSES. An unknown escape (`\\w`, `\\p`), a
    numeric one with too few digits or a digit outside its base, a surrogate and
    anything above the maximum rune are all LEX errors — measured, B1-B9 — so
    Prometheus refuses the QUERY and the panel errors rather than drawing. None
    here makes the caller refuse an expression the engine also refuses, which is
    the same fail-closed direction the unbalanced quote already pays.

    THE ESCAPABLE QUOTE IS THE OPENING ONE. `\\'` inside a double-quoted string is
    a lex error and so is `\\"` inside a single-quoted one (C1/C2), which the old
    table accepted — the same layer's over-acceptance in the other direction. A
    backtick string is RAW and no escape in it is processed at all (C4).

    THE DECLARED BOUND: `\\xNN` above 0x7F inserts a raw BYTE in Go and `chr()`
    gives the code point, so `"caf\\xe9"` and `"caf\\u00e9"` are different strings
    to the parser and the same string here (G1/G2). It needs a non-ASCII byte;
    every construct that could fool the POSIX detector is ASCII (`[`, `:`,
    letters), and so are both probes this file ever decodes for
    (`show_episode`, `plex@file`) — the same probe-bounds argument that closes
    `\\w`/`\\d`/`^`/`$` one layer up.
    """
    if len(token) < 2 or token[0] not in "\"'`" or token[-1] != token[0]:
        return None
    quote, body = token[0], token[1:-1]
    if quote == "`":
        return body
    out, i = [], 0
    while i < len(body):
        if body[i] != "\\":
            out.append(body[i])
            i += 1
            continue
        if i + 1 >= len(body):
            return None
        escape = body[i + 1]
        if escape == quote or escape in _PROMQL_SIMPLE_ESCAPES:
            out.append(_PROMQL_SIMPLE_ESCAPES.get(escape, escape))
            i += 2
            continue
        if escape in _PROMQL_OCTAL_DIGITS:
            # The first digit is part of the number, so the three of them start
            # AT it and `\101` is `A` rather than a NUL and two characters (A11).
            width, base, ceiling, first = 3, 8, 0xFF, i + 1
        elif escape in _PROMQL_NUMERIC_ESCAPES:
            width, base, ceiling = _PROMQL_NUMERIC_ESCAPES[escape]
            first = i + 2
        else:
            return None
        chunk = body[first:first + width]
        digits = _PROMQL_OCTAL_DIGITS if base == 8 else _PROMQL_HEX_DIGITS
        if len(chunk) < width or any(c not in digits for c in chunk):
            return None
        value = int(chunk, base)
        if value > ceiling or 0xD800 <= value < 0xE000:
            return None
        out.append(chr(value))
        i = first + width
    return "".join(out)


def _promql_split_matchers(inner: str) -> list:
    """The comma-separated entries of a matcher block, skipping quoted strings."""
    parts, start, i = [], 0, 0
    while i < len(inner):
        if inner[i] in "\"'`":
            i = _promql_skip_quoted(inner, i)
            continue
        if inner[i] == ",":
            parts.append(inner[start:i])
            start = i + 1
        i += 1
    parts.append(inner[start:])
    return parts


def _promql_matchers(block: str | None) -> list | None:
    """A `{…}` block as `(name, op, value)` triples, or None if it is not one.

    THE TWO CHECKS BELOW USED TO ASK THIS QUESTION WITH `in`, AND A SUBSTRING TEST
    IS NOT A MATCHER TEST. Both spelled a wanted matcher as text and looked for it
    anywhere in the block, so a typo in the label NAME satisfied them:
    `plex_media_count{mediatype!="show_episode"}` was GREEN while the engine
    returned 60 against a true 10 (calibration B14) — a `!=` on a label nothing
    carries matches EVERY series, so the panel is never empty and always wrong —
    and `…_bucket{exported_service="plex@file"}` was GREEN with `service`
    unconstrained (B18: that one selects nothing, so it is merely empty, which is
    the lesser harm and the same mechanism). Parsing the block ANCHORS every name
    at a matcher boundary by construction.

    A QUOTED LABEL NAME IS THE BARE NAME, IN A MATCHER TOO. PromQL 3.x accepts
    `{"type"!="show_episode"}`, `{'type'!='show_episode'}` and the backtick
    flavour, and the parser normalises all three to `{type!="show_episode"}`
    (calibration A1/A2/A3; the engine returns the delivered panel's own 10 for the
    quoted spelling, B13). Round 4 taught `_promql_label_set` to unquote a GROUPING
    clause and stopped there, which broke its own rule from the round before
    (`mem-1785502996-d42e`): when a tokeniser is fixed for one token class, ask the
    parser what it normalises for EVERY class the check reads.

    FAIL-CLOSED, AND THE PARSER AGREES WITH THE REFUSAL. None comes back for
    anything that is not a list of matchers — an unbalanced quote on a name (A8),
    an unquoted value (A9), a name with no operator (A10). All three are parse
    errors in Prometheus itself, so a caller that reddens on them is refusing an
    expression the engine also refuses. The legal edges are accepted and measured:
    interior whitespace (A5), a trailing comma (A6) and an empty block (A7), which
    comes back as `[]` — the bare selector, not "no opinion".

    A BARE STRING ENTRY IS THE METRIC NAME, and it comes back as the `__name__`
    equality the parser normalises it to. `{"plex_media_count", type!="show_episode"}`
    is PromQL 3.x's spelling of the DELIVERED expression: measured on
    `prom/prometheus:v3.12.0` over the 7/3/50 fixture it draws the same true 10
    (`logs/calibration-step04c-r10-name-in-braces-grammar.log` A4), and the entry
    is legal FIRST, LAST or in the MIDDLE of the list (B1/B2) in all three quote
    flavours (A4/B4/B5). Round 9 left this spelling unread and called that a bound;
    it is not a bound when the reader that meets it prints a sentence about a
    matcher block it says does not exist — see `_metric_selector`.

    THE DECLARED BOUND IS NARROWER AND IT IS LOUD: two DIFFERENT bare names in one
    block come back as two contradictory `__name__` equalities here, and the engine
    refuses the expression outright (B3, a parse error) — so the panel ERRORS
    rather than drawing a plausible number, which is the class this file prices as
    visible harm. An UNQUOTED bare name is refused in both places (B6).
    """
    if block is None:
        return None
    inner = block.strip()
    if not (inner.startswith("{") and inner.endswith("}")):
        return None
    matchers = []
    for part in _promql_split_matchers(inner[1:-1]):
        if not part.strip():
            continue
        bare = _promql_bare_metric_name(part)
        if bare is not None:
            matchers.append((PROMQL_NAME_LABEL, "=", bare))
            continue
        found = _PROMQL_MATCHER.match(part)
        if not found:
            return None
        name = found.group("name")
        if name[0] in "\"'`":
            name = _promql_unquote(name)
        value = _promql_unquote(found.group("value"))
        if name is None or value is None:
            return None
        matchers.append((name, found.group("op"), value))
    return matchers


def _promql_bare_metric_name(entry: str) -> str | None:
    """The metric name an entry of a matcher block spells BARE, or None.

    One string literal and nothing else. `_promql_skip_quoted` has to land on the
    END of the entry for it to be one: `"a" "b"` is not a bare name, and neither
    is a literal with no closing delimiter, which runs off the end and comes back
    short. The unquoting is `_promql_unquote`'s, so the escape grammar is the
    lexer's here too.
    """
    token = entry.strip()
    if not token or token[0] not in "\"'`":
        return None
    if _promql_skip_quoted(token, 0) != len(token):
        return None
    return _promql_unquote(token)


def _promql_literal_closed(text: str, start: int) -> bool:
    """Did the literal opening at `start` meet its closing delimiter?

    Asked of the SAME scanner over the text plus one character that is neither a
    quote nor a backslash: a literal that closed does not care what follows it and
    comes back with the same index, while one that ran off the end swallows the
    extra character too. That is why this is a comparison and not a look at the
    last character — `"abc\\"` ends in a quote that is ESCAPED, and the eye-test
    would call the one unterminated spelling this file has already been bitten by
    closed (`_promql_skip_quoted`, round 8).
    """
    return _promql_skip_quoted(text, start) == _promql_skip_quoted(text + " ", start)


def _promql_quoted_span(text: str, index: int) -> tuple | None:
    """The string literal containing `index`, as `(start, stop)`, or None.

    The scan starts at the beginning of the expression because a quote is only a
    quote where the lexer meets one — a `"` INSIDE a literal opens nothing. Line
    comments are already spaces by the time any row asks (`_promql_strings`).
    """
    i = 0
    while i < len(text):
        if text[i] in "\"'`":
            stop = _promql_skip_quoted(text, i)
            if i <= index < stop:
                return (i, stop)
            i = stop
            continue
        i += 1
    return None


def _promql_enclosing_matcher_block(text: str, index: int) -> tuple | None:
    """The `{…}` block containing `index`, as `(block, start)`, or None.

    Matcher blocks do not nest, so the first block that spans `index` is the only
    one. `_label_matchers` finds each block's end past quoted values, so a `}` in
    a label value neither closes a block here nor hides one.
    """
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "\"'`":
            i = _promql_skip_quoted(text, i)
            continue
        if ch == "{":
            block = _label_matchers(text, i)
            if block and i < index < i + len(block):
                return (block, i)
            i += len(block) if block else 1
            continue
        i += 1
    return None


def _promql_block_names_metric(block: str, offset: int) -> bool:
    """Is `offset` inside the entry of `block` that names the METRIC?

    TWO ENTRIES NAME A METRIC and everything else in a block names a LABEL: the
    value of a `__name__` matcher, and the bare string entry the parser
    normalises to one. An occurrence anywhere else — a label NAME, or another
    label's VALUE — is not a selector of that family at all, which is a fact
    about the rows and not a nicety: `sum(plex_sessions_count{title=
    "plex_media_count"})` returns no `plex_media_count` sample whatsoever
    (`logs/calibration-step04c-r10-name-in-braces-grammar.log` C4), so a reader
    that treated the mention as a selector would be describing a series the query
    never touches.

    The `__name__` half is asked of the VALUE's own span rather than of the entry,
    so `{__name__="x", title="plex_media_count"}` answers for each occurrence
    separately, and the label name is unquoted first because a quoted label name
    IS the bare one (C1, and `_promql_matchers`' own rule).
    """
    inner = block[1:-1] if block.endswith("}") else block[1:]
    at = offset - 1
    pos = 0
    for part in _promql_split_matchers(inner):
        if pos <= at < pos + len(part):
            if _promql_bare_metric_name(part) is not None:
                return True
            found = _PROMQL_MATCHER.match(part)
            if found is None:
                return False
            name = found.group("name")
            if name[0] in "\"'`":
                name = _promql_unquote(name)
            start, stop = found.span("value")
            return name == PROMQL_NAME_LABEL and start <= at - pos < stop
        pos += len(part) + 1
    return False


def _metric_selector(text: str, start: int, end: int) -> tuple | None:
    """The selector whose metric name occupies `[start, end)`: `(block, shown)`
    — `block` None for a selector with no matcher list — or None when that
    occurrence selects nothing.

    THE NAME MAY LIVE INSIDE THE BRACES, AND UNTIL ROUND 10 BOTH ROWS BELOW READ
    THAT SPELLING AS "no matcher block". `\\bplex_media_count\\b` matches the name
    wherever it sits, quotes included, so `_label_matchers` was asked at the
    character AFTER it — a quote — and came back None, and the row printed a
    sentence about a block it was standing inside. Measured on
    `prom/prometheus:v3.12.0` over the 7/3/50 fixture: `sum({__name__=
    "plex_media_count", type!="show_episode"})` and `sum({"plex_media_count",
    type!="show_episode"})` are ACCEPTED and draw the DELIVERED 10, and the guard
    was RED 16/17 on both, claiming "every show library EPISODE count is added to
    its title count" over expressions that exclude them
    (`logs/red-step04c-r10-name-in-braces-pre.log` A3/A4, C2/C3; the round-9
    review's `logs/critic-step04c-r9-name-in-braces.log` A3/A5/C3-C7). The sibling
    row said "carries NO label matcher — this panel graphs the whole proxy" over a
    block carrying `service="plex@file"` (F1-F3 there, C10 here).

    SO THE BLOCK IS FOUND IN EITHER DIRECTION, and the ENCLOSING one is only read
    when the occurrence is at a metric-NAME position inside it — see
    `_promql_block_names_metric` for which two entries those are and for why a
    mention in another label's value is not one.

    IT RETURNS `shown` BECAUSE THE CALLERS PRINT THE SELECTOR THEY READ. Pasting
    the name in front of a block that already contains it prints an expression
    nobody wrote, and this file's own history is that a message which does not
    match the panel is what makes a true refusal unreadable and a false one
    invisible.

    THE THIRD ANSWER IS "NOT A SELECTOR", which is None, and it is not the same as
    a selector with no block. A mention that is not at a metric-name position —
    the first argument of `count_values("plex_media_count", …)`, the target label
    of a `label_replace`, or the name used as another label's VALUE — selects no
    series of that family, and neither does an occurrence used as a label NAME.
    Both used to be read as the bare selector and answered with the bare
    selector's sentence, which reddened correct panels (C8/C9 of the round-10
    battery).

    A LEGEND IS NOT ON THAT LIST AND THE ROUND-10 SPELLING OF THIS PARAGRAPH SAID
    IT WAS. It named "a legend, an interpolated label" as cases this answers
    `None` for; measured, a `legendFormat`, a `description` and a `title` all came
    back `(None, name)` — the BARE-SELECTOR branch — and reddened correct panels
    with it (the round-10 review, `logs/critic-step04c-r10-prose-mention.log`).
    That was never a question for this function: prose is a string BESIDE the
    query, and round 11 stopped it reaching any PromQL reader at all
    (`_promql_strings`). Everything that arrives here is now a string a dashboard
    declared AS a query, which is why the list above has no prose on it.

    AND "NOT A SELECTOR" IS ONLY SAID ABOUT TEXT THIS FILE COULD READ, because a
    skip is silent and silence is how a new hole gets called a fix. Two edges fail
    CLOSED instead, both of them expressions the engine refuses outright: an
    enclosing block `_promql_matchers` cannot parse comes back as the block, so the
    caller prints its own "not a matcher list this check can read" refusal — which
    is true of it — and an occurrence swallowed by a literal that never CLOSES
    comes back as the bare selector, which is what this file answered before round
    10 and keeps the row RED rather than trading a false refusal for a silent
    accept (`logs/red-step04c-r10-name-in-braces-post.log` G1-G7). Neither is a new
    class: an unterminated literal is a lex error in every flavour, so the panel
    ERRORS rather than drawing a plausible number — the loud half of
    `_promql_calls`' declared gap and of `task-1785509072-b939`.
    """
    block = _label_matchers(text, end)
    if block is not None:
        return (block, f"{text[start:end]}{block}")
    enclosing = _promql_enclosing_matcher_block(text, start)
    if enclosing is not None:
        block, block_start = enclosing
        if _promql_matchers(block) is None:
            return (block, block)
        if _promql_block_names_metric(block, start - block_start):
            return (block, block)
        return None
    quoted = _promql_quoted_span(text, start)
    if quoted is not None and _promql_literal_closed(text, quoted[0]):
        return None
    return (None, text[start:end])


def _promql_regex_matches(pattern: str, probe: str) -> bool | str:
    """Does a PromQL `=~` pattern match `probe` — or WHY can this not say?

    THE REASON TRAVELS WITH THE VERDICT, and it has to, because there are two
    reasons and they are not the same fact about the pattern. A bool is the
    answer; a str is "cannot read this, because …". Round 6 returned a bare None
    for both and left the caller to name one of them, so `{type=~"\\\\pL+"}` — legal
    RE2, a correct pin, engine 10 — was refused with a sentence calling it a POSIX
    bracket expression while `_PROMQL_POSIX_CLASS.search` on that very pattern
    returned None: a refusal contradicted by this file's own helper. Any message
    that says "because <construct>" must be reachable from exactly one branch.

    PROMETHEUS ANCHORS A LABEL REGEX AT BOTH ENDS, so `fullmatch` is the question
    and not `search`: `type=~"show"` selects the show libraries and does NOT reach
    `show_episode` (r5 calibration B8, 3 against the 53 the unanchored reading
    would give).

    A SAMPLE OF AGREEING PATTERNS IS NOT A LICENCE. Round 5 delegated this to
    Python on the evidence that nine patterns answered the same in both engines,
    and nine agreeing patterns confirm the SHARED SUBSET and nothing else. The
    delegation is sound only over the syntax the two engines share, so the classes
    one HAS and the other LACKS are enumerated, and each one's DIRECTION is
    measured rather than assumed (`logs/calibration-step04c-r6-re2-vs-python.log`,
    55/55, `prom/prometheus:v3.12.0`, every pattern put through the real engine on
    a single-series probe carrying ONLY the synthetic type):

      * SILENT — both compile it, they MEAN different things. Exactly one class:
        POSIX bracket expressions (A1-A8). RE2 matches `show_episode` with
        `[[:alpha:]_]+` and Python does not, so the guard would call the selector
        a one-kind pin and the engine would hand the `sum` every synthetic row —
        60 against a true 10, the number this row exists for, never empty and
        therefore never visible to Step 4d's operator. This is the one class that
        has to come back None, and `_PROMQL_POSIX_CLASS` is what finds it.
      * PY-RED — Python cannot compile it, so `re.error` comes back and every
        caller reddens. `\\pL`, `\\p{L}`, `\\Q…\\E`, `\\x{73}`, `(?U)` (A9-A11,
        A13, A14). Loud, and cheap — but NOT the same fact as the row above, and
        it gets its own sentence for that reason.
      * ENGINE — RE2 refuses it, so Prometheus refuses the QUERY: Python's
        lookarounds, backreferences and `\\Z` (A15-A17). The panel errors instead
        of drawing a plausible wrong number, whatever this said about it.

    THE PROBE IS WHAT BOUNDS THE REST. `show_episode` is ASCII and carries no
    newline, so RE2's ASCII-only `\\w`/`\\d`/`\\s` and Python's Unicode-aware ones
    cannot disagree about it, and neither can `^`, `$` or `(?m)` (B0-B6). `\\z` is
    the one row that moves with the interpreter — Python 3.14, which is this
    gate's venv, means by it what RE2 means; an older `re` calls it a bad escape —
    and BOTH of those directions are safe, which is the only property needed here.

    THE STRING LAYER UNDERNEATH IS `_promql_unquote`'s, AND IT WAS THE SAME
    DEFECT ONE FRAME DOWN. A double-quoted PromQL string is escape-processed by
    the lexer before RE2 sees it, so what arrives here is a DECODED pattern —
    which round 6 relied on for `\\\\w` and did not measure for the escapes the
    lexer actually implements, leaving `[[\\x3aalpha\\x3a]_]+` to reach this
    function with no `[:` in it. Read that docstring before trusting this one:
    the enumeration below is over the pattern the ENGINE compiles only for as
    long as the decoder is faithful to the lexer.

    THE PRICE, DECLARED: `[:alpha:]` OUTSIDE a bracket expression is a plain
    character set in both engines (C12), and the detector fires on it anyway. That
    is a false refusal — loud, one allow-list line to undo, and of a pattern
    nobody writes — which is the direction every unknown case in this file already
    pays.
    """
    if _PROMQL_POSIX_CLASS.search(pattern):
        return ("is a POSIX bracket expression, which Prometheus compiles with RE2 and this "
                "gate's `re` reads as a literal character set — so what it admits is not "
                "known here")
    try:
        return re.fullmatch(pattern, probe) is not None
    except re.error as exc:
        return (f"is a pattern this gate's `re` refuses to compile ({exc}), while the RE2 "
                "Prometheus compiles it with may well accept it — so what it admits is not "
                "known here")


def _promql_split_args(text: str) -> list:
    """A call's argument list, split at TOP-LEVEL commas.

    `_promql_split_matchers` next door splits a MATCHER block, where nothing
    nests, so it skips quoted strings and nothing else. An argument list does
    nest — `label_values(pve_up{id=~"lxc/.*"}, id)` carries a comma-free matcher
    block today and `label_values(label_replace(a, "b", "c", "d", "e"), n)` a
    five-comma call tomorrow — so the depth is counted here. Splitting without it
    would read the delivered drop-down's own selector as two arguments the moment
    a second matcher was added to it.
    """
    args, start, depth, i = [], 0, 0, 0
    while i < len(text):
        char = text[i]
        if char in "\"'`":
            i = _promql_skip_quoted(text, i)
            continue
        if char in "({[":
            depth += 1
        elif char in ")}]":
            depth -= 1
        elif char == "," and depth == 0:
            args.append(text[start:i])
            start = i + 1
        i += 1
    args.append(text[start:])
    return args


def _promql_matcher_blocks(text: str) -> list:
    """Every `{…}` matcher block in an expression, as (block, start).

    The plural of `_promql_enclosing_matcher_block`, which asks the same scan
    about ONE index. The caller below has no index to ask about — it is looking
    for every place the expression constrains a label, wherever the selector that
    opened it sits — so the scan is shared and the question differs, which is
    this file's rule for a walk (DEC-085). `_label_matchers` finds each block's
    end past quoted values, so a `}` inside a label value neither closes a block
    nor hides one.
    """
    out = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in "\"'`":
            i = _promql_skip_quoted(text, i)
            continue
        if char == "{":
            block = _label_matchers(text, i)
            if block is None:
                i += 1
                continue
            out.append((block, i))
            i += len(block)
            continue
        i += 1
    return out


def _grafana_label_values(text: str) -> list:
    """Every `label_values(…)` call in a variable's query: (selector, label).

    The selector is None for the one-argument spelling, which selects nothing in
    particular — Grafana asks for the label's values across the WHOLE TSDB. An
    arity Grafana's own parser does not accept comes back `(None, None)` so the
    caller reports it rather than reading the first argument as a label.

    THE CALL IS FOUND BY `_promql_calls`, so a `#` comment cannot spell one and
    a quoted `label_values(` inside a label value is not one — both are already
    true of every other reader here because the text arrives through
    `_promql_strings`. What this does NOT do is claim the argument is a legal
    PromQL selector; that is `test_delivered_dashboard_queries_are_readable`'s,
    and the row below only asks what the selector ADMITS.
    """
    out = []
    for head, _clause, _labels, start, end in _promql_calls(text):
        if head != GRAFANA_LABEL_VALUES:
            continue
        args = [arg.strip() for arg in _promql_split_args(text[start + 1:end])]
        if len(args) == 1:
            out.append((None, args[0]))
        elif len(args) == 2:
            out.append((args[0], args[1]))
        else:
            out.append((None, None))
    return out


def _pve_id_admits(matchers: list, probe: str) -> bool | str:
    """Do a selector's `id` matchers admit `probe` — or WHY can this not say?

    The reason travels with the verdict for `_promql_regex_matches`' reason: a
    pattern this gate's `re` reads differently from RE2 is not a "no", and a
    caller that flattened it into one would refuse a working drop-down with a
    sentence about the wrong thing.

    EVERY `id` MATCHER MUST ADMIT IT, which is how Prometheus reads a selector —
    the matchers are ANDed — and the negative operators are read rather than
    skipped, because `{id!="node/pve"}` is a selector that admits every container
    AND every other guest, which is the C1-shaped mutation one operator over.
    Matchers on any other label are not this function's question: they narrow the
    SERIES, not the values of `id`, and a drop-down scoped by
    `{id=~"lxc/.*", node="pve"}` still yields container ids.
    """
    for name, op, value in matchers:
        if name != PVE_GUEST_LABEL:
            continue
        if op == "=":
            admits = value == probe
        elif op == "!=":
            admits = value != probe
        elif op in PROMQL_REGEX_OPERATORS:
            verdict = _promql_regex_matches(value, probe)
            if isinstance(verdict, str):
                return f"pins {PVE_GUEST_LABEL} with {value!r}, which {verdict}"
            admits = verdict if op == "=~" else not verdict
        else:
            return f"pins {PVE_GUEST_LABEL} with the operator {op!r}, which this gate cannot read"
        if not admits:
            return False
    return True


def _pve_selector_yields_containers(selector: str | None) -> str | None:
    """None if a `label_values` selector yields the containers, else WHY not.

    THREE WAYS TO YIELD SOMETHING OTHER THAN THE CONTAINER LIST, and all three
    render as a drop-down that looks fine:

      * a family the pinned exporter does not emit — the drop-down is EMPTY, and
        `test_pve_panels_name_series_the_exporter_declares` cannot see it when
        the near-miss is not a `pve_` token at all (`node_up`), because that row
        is keyed on the prefix;
      * a scope that has lost `lxc/` — every node, QEMU guest and storage the
        cluster has, listed under a drop-down labelled Container;
      * a scope narrowed past one of the two containers the Test Requirement
        names, which is the same edit in the other direction.

    The metric name is read in FRONT of the block or as the `__name__` equality
    `_promql_matchers` normalises a name-in-braces to, so PromQL 3.x's spelling
    of the same selector answers the same.
    """
    if selector is None:
        return (f"is the one-argument spelling, which asks for every value of "
                f"{PVE_GUEST_LABEL!r} in the whole TSDB rather than the guests of one family")
    blocks = _promql_matcher_blocks(selector)
    matchers = _promql_matchers(blocks[0][0]) if blocks else []
    if matchers is None:
        return f"carries the matcher block {blocks[0][0]!r}, which this gate cannot read"
    ident = _PROMQL_IDENT.match(selector.strip())
    family = ident.group(0) if ident else None
    for name, op, value in matchers:
        if name == PROMQL_NAME_LABEL and op == "=":
            family = value
    if family not in PVE_EXPORTER_SERIES:
        return (f"selects {family!r}, which is not one of the {len(PVE_EXPORTER_SERIES)} families "
                "prompve/prometheus-pve-exporter:3.9.0 declares — the drop-down would be empty")
    for probe in PVE_TEST_REQUIREMENT_GUESTS:
        verdict = _pve_id_admits(matchers, probe)
        if isinstance(verdict, str):
            return verdict
        if not verdict:
            return (f"does not admit {probe!r}, one of the two containers Step 4's Test "
                    "Requirement names")
    for probe in PVE_NON_CONTAINER_IDS:
        verdict = _pve_id_admits(matchers, probe)
        if isinstance(verdict, str):
            return verdict
        if verdict:
            return (f"admits {probe!r}, which is not a container — the `lxc/` scope that makes "
                    "this a CONTAINER drop-down is gone")
    return None


def _grafana_variable_alternates(var: dict) -> list:
    """The keys letting this `templating.list[]` entry interpolate MORE THAN ONE value.

    A LIST AND NOT A BOOLEAN, so the caller's message can name the key an
    operator has to undo — `includeAll` and `multi` are separate checkboxes in
    the variable editor and a dashboard can carry either, or both, and the repair
    is different in each case.

    JS TRUTHINESS, NOT `is True`, and that is measured rather than assumed:
    Grafana's own gate is `if (!variable.multi && !variable.includeAll)` over the
    JSON scalar, reached with `isMulti` passed through RAW — see
    `GRAFANA_VARIABLE_ALTERNATING_KEYS` for the whole chain and
    `GRAFANA_FALSY_VALUES` for the twelve values node and this tuple were made to
    agree on. `multi: "false"` is a TRUE flag to Grafana; `multi: 0` is not one.

    WHY THIS IS NOT A CLAUSE OF `_pve_container_drop_down`. Every other refusal
    in that classifier is a property of the entry alone: a `custom` type, a live
    `regex`, `hide: 2` are wrong whatever the panels say. These two are not — an
    All selection interpolates a regex alternation, which is exactly right for a
    `=~` panel and fatal for a `=` one, so the defect is a RELATION between this
    entry and the matchers that read it. Refusing the key here would forbid the
    ordinary multi-select Grafana dashboard; the caller asks the second half.
    """
    return [key for key in GRAFANA_VARIABLE_ALTERNATING_KEYS
            if var.get(key) not in GRAFANA_FALSY_VALUES]


def _grafana_variable_all_value(var: dict):
    """The string this entry pastes RAW when All is selected, or None.

    THE VALUE AND NOT A BOOLEAN, because the caller's message has to show the
    operator what it is: `.*` graphs the whole cluster, `node/.*` graphs the
    node, and `lxc/.*` is the working dashboard this refusal costs — three very
    different sentences about one key.

    THE SAME JS TRUTHINESS AS `_grafana_variable_alternates`, and for the same
    measured reason: Grafana's gate is `if (this.state.allValue)` on whatever the
    JSON held, so `GRAFANA_FALSY_VALUES` is reused rather than a second predicate
    invented (`logs/calibration-step05d-rework-r4-allvalue.py` B4 — node and that
    tuple agree on all eleven scalars). `allValue: ""` is what the variable
    editor leaves behind and is NOT a set key.

    WHY THIS IS NOT CONDITIONED ON `includeAll`, which is the shape it looks like
    it should have: see `GRAFANA_VARIABLE_ALL_VALUE_KEY`. The picker can only
    reach All through that key, but `updateFromUrl` cannot be reached through the
    picker at all — a link's `?var-guest=$__all` survives the validation that
    would reset it (A5/A6), and the allValue string is itself a URL spelling of
    All (A7). A rule over the pair would call that file inert.
    """
    value = var.get(GRAFANA_VARIABLE_ALL_VALUE_KEY)
    return None if value in GRAFANA_FALSY_VALUES else value


def _panel_repeats_over(clauses: list, where: str, name: str) -> bool:
    """True if the panel CARRYING this query repeats over the variable `name`.

    THE ONE STATE IMMUNE TO EVERY ALTERNATING KEY, and it is a different READER
    inside Grafana rather than an argument about the same one: `performRepeat`
    asks `getMultiVariableValues`, which returns `options.map(o => o.value)` — the
    ids — without ever calling `getValue()`, so neither the `(lxc/110|lxc/111)`
    alternation nor the `allValue` is on that path at all (calibration A8). Every
    clone, the source panel included (`index === 0`), is then given a
    `LocalValueVariable` holding ONE of those ids, which shadows the drop-down
    for that panel's queries (A9/A10). `repeat: "guest"` with the delivered
    `{id="$guest"}` is the canonical Grafana per-container idiom and it WORKS
    (engine C7) — round 3 reddened it, and DEC-137's "the narrow rule has no
    false side" was false.

    EXEMPTED RATHER THAN DECLARED AS A PRICE, which the review offered as the
    cheaper option, because the panel is not merely tolerable — it is correct,
    and no edit to it would make the guard's complaint true. The bound is that
    the clone's id goes through `prometheusSpecialRegexEscape` (the
    `LocalValueVariable` carries `includeAll` through), and the exporter's ids
    are fixed points of that class while an id carrying a regex metacharacter
    would not be (B1/B2/B3).

    CONTAINMENT IS A SET OF JSON-PATH PREFIXES, one of which is always the
    clause's own carrier: `$.panels[3].repeat` covers
    `$.panels[3].targets[0].expr`, and a COLLAPSED repeating row covers the
    `$.panels[3].panels[7].targets[0].expr` of the panels nested in it. A repeat
    over a DIFFERENT variable — or over this one on a different panel — covers
    nothing.

    AND A PREFIX IS NOT ENOUGH FOR THE SPELLING GRAFANA ACTUALLY WRITES, which
    is round 4's review and this round's repair. An EXPANDED row saves
    `panels: []` and its children are the SIBLINGS that follow it, at
    `$.panels[4]…` — no prefix of `$.panels[3]` reaches them, so the canonical
    per-container dashboard, built the way the row-repeat UI builds it, was
    refused on all thirteen targets while the collapsed byte-twin passed. The
    span is `_grafana_row_span`, computed in the same walk, and it is bounded on
    every side a review can ask about: it starts after the row, stops at the next
    row, never leaves its own `panels[]` list, is asked only of a row that
    `Boolean(collapsed)` says is expanded, and "after" means after in the order
    Grafana walks — `(gridPos.y, gridPos.x)`, the SCREEN's order, since
    `DashboardModel`'s constructor sorts the list before that loop ever sees it.

    `_dashboard_repeat_clauses` is the reader, shared with the declared-name row
    so the two cannot drift apart — that row reads the first two members, this
    one the third.
    """
    return any(clause == name and any(where.startswith(f"{at}.") for at in covers)
               for _where, clause, covers in clauses)


def _pve_container_drop_down(var: dict, texts: list) -> str | None:
    """None if this `templating.list[]` entry is the container drop-down, else WHY not.

    ONE CLASSIFIER, ASKED OF EVERY QUERY THE ENTRY CARRIES. `definition` and
    `query`/`query.query` are two spellings of one variable's query and Grafana
    runs the second; an entry whose two halves disagree is a drop-down that does
    not do what the file says it does, so EVERY query the entry declares has to
    yield the containers and at least one has to exist. Accepting the entry
    because one of its two halves is right would wave through the commonest way
    to half-edit a variable by hand.

    A NON-`query` VARIABLE IS REFUSED AND THE PRICE IS DECLARED. A `custom`
    variable listing `lxc/110,lxc/111` renders a drop-down that reads correct
    TODAY and is a hardcoded pair of strings: it will keep offering CT 111 after
    that container is destroyed, and it will never learn about a third. The Test
    Requirement is about what the drop-down LISTS, and gate 2b's whole acceptance
    is that those values come from `pve_up` — so the refusal is loud, one word to
    undo, and in the direction this file pays everywhere else.

    AND THE QUERY IS NOT THE ONLY KEY THAT DECIDES WHAT THE OPERATOR SEES. Two
    more of the delivered entry's twelve keys sit BETWEEN the values the query
    returns and the values the drop-down offers, and each of them empties Step 4's
    Test Requirement while every clause above is satisfied — see
    `GRAFANA_HIDE_VARIABLE_VALUES` for both mechanisms read out of the pinned
    Grafana. They are refused here rather than modelled, and the shape of each
    refusal is chosen for its FALSE side:

      * A NON-EMPTY `regex` IS REFUSED WHATEVER IT SAYS, and `regex: ".*"` is a
        real false refusal — it matches every value, carries no capture group and
        would change nothing. Modelling "a pattern that provably keeps both ids
        whole" means deciding, for an arbitrary JS regex, whether it matches two
        strings and whether any of its capture branches fires; the version of
        that question this file already answers (`_promql_regex_matches`) exists
        for RE2 and returns "cannot say" often enough to need its own reason
        channel. So the refusal is the whole non-empty class: loud, one word to
        undo, scored as D2 of `logs/red-step05d-rework-r2.py` so the price is on
        the record, and widening it later is additive. The value is NOT stripped
        first — `regex: " "` is truthy to Grafana and anchors to `/^ $/`, which
        matches nothing and empties the drop-down (D1).
      * `hide` IS REFUSED ON ONE VALUE, not on "not zero". `hideVariable` renders
        no picker while the variable keeps interpolating, so every panel reads it
        and the operator has nothing to choose with — the Test Requirement gone
        with the dashboard otherwise perfect. `hideLabel` and `inControlsMenu`
        keep the control and stay GREEN (B4/B5).

    AND TWO MORE KEYS OF THE SAME CLASS ARE NOT ANSWERED HERE, ON PURPOSE.
    `includeAll`, `multi` and `allValue` also stand between the query and the
    panels, and they are the reason this docstring cannot end at "the entry
    decides": an All selection substitutes BOTH ids as a regex alternation, which
    is right for a `=~` panel and fatal for a `=` one, and an `allValue` replaces
    the whole substitution with a raw string — while a panel REPEATING over the
    variable is immune to all three. Every one of those is a RELATION between the
    entry and the panels, and this classifier never sees a panel, so it is the
    wrong place to price them. They are checked in the caller's matcher walk; see
    `_grafana_variable_alternates`, `_grafana_variable_all_value` and
    `_panel_repeats_over`. The general lesson rounds 3 and 4 paid for is written
    down as a rule rather than a patch: WHEN A REVIEW NAMES N KEYS OF A CARRIER,
    THE ROUND'S SCOPE IS THE CARRIER — and a key already priced is re-priced when
    the rule's shape moves, because a pricing is evidence about a shape. Rounds 1
    and 2 answered `regex` and `hide` and left the rest unasked; round 3's review
    found key three; round 4's found key four sitting on the priced list with a
    reason measured against a rule that was never built. The whole delivered
    entry is enumerated and priced in `GRAFANA_PVE_DROP_DOWN_KEYS_PRICED`.

    WHAT THIS DELIBERATELY DOES NOT REFUSE, MEASURED RATHER THAN ASSUMED:
    `refresh: 0` ("never"). It looks like the same class — a saved `options` array
    frozen in place of the query's answer — and in this runtime it is not one:
    `QueryVariable.getValueOptions` guards on the QUERY and never on `refresh`,
    and the only place the variable set reads `refresh` is the time-range re-run
    (calibration F1/F2). It stays GREEN, scored as B9.
    """
    if var.get("type") != GRAFANA_QUERY_VARIABLE_TYPE:
        return (f"is a {var.get('type')!r} variable, not a {GRAFANA_QUERY_VARIABLE_TYPE!r} one — "
                "its values are typed into the dashboard rather than read from the exporter")
    regex = var.get(GRAFANA_VARIABLE_REGEX_KEY)
    if regex not in GRAFANA_FALSY_VALUES:
        return (f"carries {GRAFANA_VARIABLE_REGEX_KEY}: {regex!r}, and Grafana filters the values "
                "the query returned through it before the drop-down offers them — a value the "
                "pattern does not match is dropped from the list and a capture group rewrites it, "
                "so what the operator picks from is not what the query yields")
    hide = var.get(GRAFANA_VARIABLE_HIDE_KEY)
    if hide in GRAFANA_HIDE_VARIABLE_VALUES:
        return (f"declares {GRAFANA_VARIABLE_HIDE_KEY}: {hide!r}, which renders no picker at all — "
                "the variable keeps interpolating, so every panel still reads it and the operator "
                "has nothing to choose with")
    seen = 0
    for text in texts:
        calls = _grafana_label_values(text)
        if not calls:
            return (f"declares the query {text!r}, which calls no {GRAFANA_LABEL_VALUES}() — this "
                    "gate cannot say what values it would offer")
        for selector, label in calls:
            seen += 1
            if label != PVE_GUEST_LABEL:
                return (f"declares the query {text!r}, which yields the label {label!r} and not "
                        f"{PVE_GUEST_LABEL!r} — the panels match its values against "
                        f"{PVE_GUEST_LABEL!r}")
            why = _pve_selector_yields_containers(selector)
            if why is not None:
                return f"declares the query {text!r}, which {why}"
    if not seen:
        return (f"declares no query at all in {list(GRAFANA_VARIABLE_QUERY_KEYS)} — a "
                f"{GRAFANA_QUERY_VARIABLE_TYPE!r} variable with no query offers nothing")
    return None


def _promql_head_kind(head: str) -> str | None:
    """How a call head treats the labels it is handed, or None if nobody knows.

    ONE CLASSIFIER, TWO CHECKS, so they cannot disagree. Both rows below ask the
    same question of a call — does this thing MERGE series that must stay apart —
    and round 2 answered it twice, in two branches, which is how they ended up
    treating an unclassified head differently: the histogram row made it RED and
    the library row let it through. A shared function makes the answer a property
    of the classification instead of a coincidence between two edits.

    THE UNKNOWN CASE IS THE CALLER'S TO PRICE, and both callers price it RED.
    The list cannot be complete — `limitk` and `limit_ratio` are aggregations
    Prometheus 3.x already ships behind `--enable-feature=promql-experimental-
    functions` (calibration A6) and would admit tomorrow — so incompleteness
    costs one line here and a loud refusal naming the head, rather than a silent
    pass over a panel that is wrong and not empty.

    SELECTION IS CHECKED FIRST, AND THE OVERLAP IS DELIBERATE. `topk`/`bottomk`
    are in `PROMQL_AGGREGATION_OPERATORS` because they are what that set says
    they are — heads the parser accepts a grouping modifier on (round-4
    calibration A7) — and they are in `PROMQL_SERIES_SELECTING_OPERATORS`
    because that is the question the callers actually ask: do they MERGE series
    that must stay apart. They do not (C1-C4). Keeping the first set honest to
    the parser and answering the callers' question with the second is why the
    order here matters.
    """
    if head.lower() in PROMQL_SERIES_SELECTING_OPERATORS:
        return PROMQL_HEAD_SELECTING
    if head.lower() in PROMQL_AGGREGATION_OPERATORS:
        return PROMQL_HEAD_AGGREGATION
    if head == PROMQL_HISTOGRAM_QUANTILE:
        return PROMQL_HEAD_QUANTILE
    if head in PROMQL_LABEL_TRANSPARENT_CALLS:
        return PROMQL_HEAD_TRANSPARENT
    return None


def _promql_subject_reaches(text: str, subject: str, span: tuple, consumers: list) -> bool:
    """Does `subject` reach the call whose argument span is `span` UNCONSUMED?

    "IS `le` STILL ALIVE AT MY LEVEL" IS THE QUESTION, not "is the bucket name
    somewhere inside my parentheses" — and the difference is a correct expression
    the round-2 row refused. `histogram_quantile` CONSUMES `le`; its result is a
    plain latency, so `max(histogram_quantile(0.90, sum by (le) (rate(…))))` is
    right and the engine returns the interpolated quantile for it (calibration
    B4/B5). Asking the name question refuses every aggregation stacked above the
    quantile, with a message about `le` that is factually false at that level.

    So an occurrence of the subject inside `span` counts only if it is NOT also
    inside a consumer call nested within `span`. `qs >= start` is what makes the
    consumer NESTED rather than merely overlapping: a quantile ABOVE this call
    (`histogram_quantile(0.5, sum by (code) (…))`, where the span belongs to the
    `sum`) starts before it, does not consume anything on this call's behalf, and
    leaves the `sum` answerable — which is why B12/R12 stay RED.

    THE BOUND: this is per-OCCURRENCE, so a call that mixes a consumed read with
    a live one — `sum by (code) (histogram_quantile(…bucket…) + rate(…bucket…))`
    — is still answerable for the live half. What it does NOT model is an
    aggregation whose only live occurrence sits behind another label-consuming
    call this file has never classified; that head is RED anyway.
    """
    start, end = span
    for match in re.finditer(re.escape(subject), text):
        pos = match.start()
        if not (start <= pos < end):
            continue
        if any(qs >= start and qs <= pos < qe for qs, qe in consumers):
            continue
        return True
    return False


def _plex_media_matcher_pins_one_kind(name: str, op: str, value: str) -> bool | str:
    """Does this ONE matcher guarantee the rows it admits are all of one kind?

    THREE ANSWERS, NOT TWO: True (it pins one kind), False (it demonstrably admits
    both) and a REASON — this check cannot READ the matcher, which is a different
    thing and must be said differently. The caller prints the reason it is handed
    rather than composing one, because a pattern nobody has decided must not
    inherit the sentence "admits real library rows AND the synthetic ones": that
    sentence is a claim about the rows, and three rounds of this file were
    rejected for refusals that were factually false. Round 6 made the value
    three-valued and still hard-coded the reason at the caller, which is the same
    defect with one more branch in front of it.

    THE RULE IS NOT "EXCLUDE THE SYNTHETIC TYPE", IT IS "THE ROWS THAT ENTER THIS
    CALL CANNOT BE OF BOTH KINDS" — and the difference is four correct panels the
    round-4 accept side refused, every one of them measured in the real engine
    (`logs/calibration-step04c-r5-matchers.log`). An EQUALITY on a distinguishing
    label admits exactly ONE value, so there is no synthetic row and a real row in
    the same call to add together at all: `{type="show_episode"}` is the EPISODE
    total the exporter synthesises that row FOR (B2, 50), `{type="movie"}` is a
    movie-library panel (B3, 7), `{type="show"}` the show libraries with no
    episodes (B4, 3), and `{title="TV"}` one library pinned by name (B5, 3),
    whose synthetic twin carries the DIFFERENT title `TV - Episodes`.

    A REGEX IS DECIDED BY ASKING IT, because PromQL anchors label regexes at both
    ends and that makes the question finite: `{type=~"movie|show"}` returns the
    true 10 (B6) since `show` does not reach `show_episode` (B8), while
    `{type=~"show.*"}` returns 53 (B9) because it does. `!~` is the mirror and
    only excludes the synthetic rows when it matches THEM: `{type!~"show_episode"}`
    is the delivered panel's 10 (B7), but `{type!~"show"}` drops the show
    libraries and KEEPS their episodes, 57 (B10). See `_promql_regex_matches` for
    why Python is allowed to answer at all, and for the two reasons it may decline
    to — both of which are returned verbatim from here, so the reader meets the
    one that is true of the pattern in front of them.

    ONLY `=` PINS ON `title`. A `!=` or a regex on a title drops a library rather
    than a kind, and the survivors are still mixed: `{title!="TV"}` is 57 (B11)
    and `{title=~"TV.*"}` is 53 (B12) — a library and its own ` - Episodes` twin.
    Nothing about `title` identifies the synthetic rows as a class; only its
    pinning to a single value does.

    THE DECLARED FALSE REFUSAL: a regex that admits the synthetic type AND NOTHING
    ELSE — `{type=~"(?i)SHOW_EPISODE"}`, engine 50 and therefore correct (B16) —
    is refused here, because "this pattern admits one value only" needs the set of
    values the label actually takes and no offline check has it. The cost is one
    loud refusal that names the `=` spelling accepted above; the alternative is
    guessing at a live label's cardinality.
    """
    if name == PLEX_MEDIA_TYPE_LABEL:
        if op == "=":
            return True
        if op == "!=":
            return value == PLEX_MEDIA_SYNTHETIC_TYPE
        if op in PROMQL_REGEX_OPERATORS:
            reaches = _promql_regex_matches(value, PLEX_MEDIA_SYNTHETIC_TYPE)
            if isinstance(reaches, str):
                return reaches
            # `=~` pins the kind by NOT reaching the synthetic type; `!~` pins it
            # by reaching exactly it, which is what makes the exclusion a mirror
            # (r5 calibration B7 against B10).
            return reaches is (op == "!~")
        return False
    if name in PLEX_MEDIA_DISTINGUISHING_LABELS:
        return op == "="
    return False


def _plex_media_mixed_selector(text: str, span: tuple) -> tuple | None:
    """Why a `plex_media_count` selector inside `span` may hand its call BOTH
    kinds of row — or None if not one of them can.

    `(demonstrated, reason)`, AND THE FLAG IS THE HALF ROUND 6 LEFT UNDONE. True
    means the rows entering the call are KNOWN to be of both kinds; False means
    this check could not read the selector and is refusing rather than asserting.
    Round 6 gave the unreadable case an honest inner clause and left the caller
    wrapping every one of them in "the panel populates and is wrong by the size of
    the TV library", which moved the false claim one frame out instead of removing
    it. A predicate that gains a third value has to be re-audited at the OUTERMOST
    place a reader meets it.

    A PREDICATE APPLIED PER-CALL MUST BE EVALUATED PER-CALL. This used to be one
    flag computed over the whole expression — set if ANY occurrence anywhere
    carried `type!="show_episode"` — and then consulted inside the per-call loop,
    so one correct `sum` exempted every other `sum` beside it. The carrier is an
    ordinary fraction-of-titles panel:
    `sum(plex_media_count{type!="show_episode"}) / sum(plex_media_count)` was
    GREEN, and the engine returns 10/60 for it (`logs/calibration-step04c-r4-
    promql-quotes-and-selection.log` D2) while the same bare `sum` standing alone
    was RED. Silent, and no new spelling was needed to reach it.

    EVERY OCCURRENCE, NOT ANY, because a call is only safe if BOTH kinds never
    enter it: `sum(plex_media_count{type!="show_episode"} + on (title, type)
    plex_media_count)` puts them back through the second operand and the engine
    returns 20 against a true 10 (D4). `any()` inside one span is the same
    quantifier mistake one scope down. Within a SINGLE selector the quantifier is
    the other way round and for the same reason: matchers narrow, so ONE of them
    pinning the kind is enough and the rest only take rows away
    (`{type!="show_episode",title="TV"}` is 3 — r5 calibration B15).

    THE BOUND, MEASURED AND LEFT OPEN ON PURPOSE: every selector in the span must
    pin ONE kind, and nothing here requires them to pin the SAME kind, while the
    sentence above says "the rows that ENTER THIS CALL cannot be of both kinds".
    Three shapes are GREEN and wrong, all measured on `prom/prometheus:v3.12.0`
    over the 7/3/50 fixture (`logs/calibration-step04c-r6-re2-vs-python.log` D1-D5):
    `sum(…{type="show_episode"} or …{type="movie"})` is 57, `sum(…{title="TV"} or
    …{title="TV - Episodes"})` is 53 against a true 3 — a library unioned with its
    own synthetic twin — and the two-call spelling `sum(…{type="movie"}) +
    sum(…{type="show_episode"})` merges at a binary operator no per-call loop can
    see at all.

    WHY IT IS NOT CLOSED HERE RATHER THAN MERELY NOTED. A same-kind rule needs
    each selector's kind, and `title` HAS no offline kind: D2 above and D5,
    `sum(…{title="Movies"} or …{title="TV"})` — two real libraries by name,
    engine 10, correct — are the SAME shape, two `title="…"` equalities in one
    call, and only the live label set separates them. So the cheap rule buys a
    silent 53 by charging a false refusal of a correct panel, in the file that has
    been rejected twice for forbidding the real answer. Filed as
    `task-1785506726-adc5` with the mechanism, the numbers and what a fix must
    prove; it needs a kind LATTICE this function does not have — and a reader for
    the binary operator, which no per-call loop reaches — not one more clause.

    IT RETURNS THE REASON, NOT A BOOLEAN, because half of what round 5 fixed was
    refusals that were factually FALSE — a message claiming episodes were added to
    titles, printed over an expression that could not have added them. The caller
    prints what came back, so an unreadable block and a genuinely mixed one do not
    get each other's sentence.

    FAIL-CLOSED IN FOUR PLACES, all of them loud and none of them silent: a
    selector with no matcher block at all, a block `_promql_matchers` cannot read
    (an unbalanced quote, an unquoted value, a name with no operator, or an escape
    the lexer rejects), a matcher whose regex this gate's `re` and the engine's
    RE2 would read differently, and one this gate's `re` cannot compile at all.
    Only the first, the empty block and a selector every matcher of which was READ
    and found wanting are `demonstrated`; the rest are refusals. An occurrence
    that is a substring of a longer name is not one (`\\b`). The caller's other
    accept path — a modifier that keeps a distinguishing label — stays open in
    every case.

    THERE USED TO BE A FIFTH, "no selector is readable in this span", AND IT WAS
    UNREACHABLE PROSE THAT DESCRIBED THE WRONG BRANCH — the round-9 review's F1.
    It claimed the `{"plex_media_count", …}` spelling arrived there because the
    name sits inside the braces; what actually happened is that `\\bname\\b` matched
    the name inside the quotes, `seen` was set, `_label_matchers` was asked at the
    character after it, and the CORRECT panel came back `demonstrated=True` with
    "carries no `{…}` matcher" — the fail-open half of this file's own rule
    printed as a false refusal. Both name-in-braces spellings draw the DELIVERED
    10 on `prom/prometheus:v3.12.0` and the guard was RED 16/17 on both
    (`logs/red-step04c-r10-name-in-braces-pre.log` A3/A4, C2/C3). `_metric_selector`
    now finds the block in either direction, so the spelling is READ rather than
    enumerated, and the branch that was never reached is gone rather than
    reworded. An occurrence that names no series at all — a mention in another
    label's value, in a `count_values` name, in a legend — is skipped, because it
    selects nothing of this family (grammar C4) and answering for it was the same
    false refusal one spelling over.

    AND ONE OF THOSE FOUR IS NEVER REACHED, WHICH IS SAID HERE BECAUSE A REFUSAL
    NOBODY ASKS FOR READS LIKE COVERAGE. A string literal with NO CLOSING
    DELIMITER hides the whole call from `_promql_calls`, whose skip-quoted scan
    runs to the end of the expression and swallows the closing paren, so
    `sum(plex_media_count{"type!="show_episode"})` produces no call at all and
    this function is not consulted — the DEC-077 shape again, a defect the
    tokeniser cannot FORM being invisible rather than rejected.

    THE BOUND IS THAT ONE SPELLING, AND IT IS STATED AS A SPELLING BECAUSE THE
    SAME SENTENCE HAS NOW BEEN WRITTEN AS AN ENUMERATION TWICE AND WAS FALSE BOTH
    TIMES. Round 7 wrote "an unbalanced quote is a lex error in Prometheus too",
    and `{type!=`\\`}` — a BALANCED, LEGAL raw string ending in a backslash —
    reached the same invisibility while the engine accepted it and drew 60
    against a true 10; that spelling is now scanned correctly
    (`_promql_skip_quoted`, measured `logs/red-step04c-r8-raw-string-scanner-
    post.log` A3/B1/C4). Round 8 then wrote "the unterminated literal is what is
    left, and it IS a lex error in every flavour", and a `#` COMMENT — which is
    not a literal, is not an error, and DRAWS — reached it in both directions;
    that class is closed too, by `_promql_blank_comments` at the one boundary
    `_promql_strings`, measured `logs/red-step04c-r9-promql-comments-post.log`
    (fail-open C3/C7/C12/C13, false refusal C10/C11, accept side C4/C5/C8/C9).

    SO THE DECLARED BOUND IS NOT "EVERYTHING ELSE IS LOUD". It is: the spelling
    `sum(plex_media_count{"type!="show_episode"})`, a literal with NO CLOSING
    DELIMITER, is a lex error in every flavour, so the engine refuses the query
    and the panel ERRORS instead of drawing a plausible number (A6/A7 of the r8
    log; `logs/calibration-step04c-r7-lexer-escapes.log` H1-H3 for the three
    unbalanced spellings). That is the argument for leaving THAT spelling
    declared, and it is an argument about that spelling only — the twice-repeated
    mistake was reading it as a census of what else can be invisible. Filed as
    `task-1785509072-b939` with what a fix must prove, including the accept side
    of the two sibling rows that read the same scanner — re-measured this round
    on the real dashboard (C4/C5/C8) because the readers moved under them.
    """
    start, end = span
    for match in re.finditer(rf"\b{PLEX_MEDIA_COUNT}\b", text):
        if not (start <= match.start() < end):
            continue
        selector = _metric_selector(text, match.start(), match.end())
        if selector is None:
            continue
        block, shown = selector
        if block is None:
            return (True,
                    f"`{shown}` carries no `{{…}}` matcher, so it selects the whole "
                    "family — the exporter's synthetic episode rows included")
        matchers = _promql_matchers(block)
        if matchers is None:
            return (False,
                    f"`{shown}` is not a matcher list this check can read — an "
                    "unbalanced quote, an unquoted value, a name with no operator or a string "
                    "escape the PromQL lexer rejects, each of which the Prometheus parser also "
                    "refuses")
        if not matchers:
            return (True,
                    f"`{shown}` is the bare selector written with an empty "
                    "block, so it selects the whole family")
        verdicts = [(one, _plex_media_matcher_pins_one_kind(*one)) for one in matchers]
        if any(verdict is True for _, verdict in verdicts):
            continue
        # A matcher that PINS the kind settles the selector even beside one nobody
        # can read, because matchers only narrow (`{type!="show_episode",title=
        # "TV"}` is 3 — r5 calibration B15). So True is taken first and a reason
        # is only reached when nothing else answered.
        undecidable = [(one, why) for one, why in verdicts if isinstance(why, str)]
        if undecidable:
            (name, op, value), why = undecidable[0]
            return (False,
                    f"`{shown}` cannot be decided by this check: `{name}{op}"
                    f'"{value}"` {why}. Pin the kind with an equality '
                    f'(`{PLEX_MEDIA_TYPE_LABEL}="{PLEX_MEDIA_SYNTHETIC_TYPE}"`), exclude the '
                    f"synthetic rows (`{PLEX_MEDIA_EXCLUDED}`), or write the pattern in the "
                    "syntax both engines share")
        return (True,
                f"`{shown}` admits real library rows AND the synthetic "
                f"`{PLEX_MEDIA_SYNTHETIC_TYPE}` ones: no matcher on "
                f"{sorted(PLEX_MEDIA_DISTINGUISHING_LABELS)} either keeps the synthetic type "
                "out or pins the label to a single value")
    return None


def test_guarded_files_exist() -> bool:
    missing = [str(p.relative_to(REPO_ROOT)) for p in (TASKS, COMPOSE, DATASOURCE_TPL, DASHBOARDS_TPL)
               if not p.is_file()]
    ok = not missing
    print(f"{'OK' if ok else 'FAIL'}: grafana provisioning sources present (missing={missing})")
    return ok


def test_grafana_service_keeps_the_root_group() -> bool:
    """The compose service must not drop the container out of gid 0.

    THE COMPANION OF THE MODE CHECKS, and the reason they can accept `0640`.
    The delivered tree is owned `root:root`, so the only bits that answer for
    this container are the GROUP bits, and they answer only while the process
    keeps gid 0. Measured: the delivered tree read as `472:0` is READABLE (row
    B1) and the SAME tree read as `472:472` is DENIED (row B4). An override is
    therefore not forbidden — one that keeps gid 0 (`user: "472:0"`) is fine and
    passes here; one that does not, does not.
    """
    body = _read(COMPOSE)
    if body is None:
        print("FAIL: grafana service keeps gid 0 (compose.yml.j2 unreadable)")
        return False
    block = _compose_service_block(body, GRAFANA_SERVICE)
    if not block:
        print(f"FAIL: grafana service keeps gid 0 (no `{GRAFANA_SERVICE}:` service in compose.yml.j2)")
        return False
    user = _scalar(block, "user")
    if user is None:
        print(f"OK: grafana service declares no `user:` -> image default {GRAFANA_UID}:0 applies")
        return True
    gid = user.split(":")[1] if ":" in user else None
    ok = gid is not None and gid.strip() in ("0", "root")
    print(f"{'OK' if ok else 'FAIL'}: grafana service `user: {user}` keeps gid 0 "
          f"(root-group bits are what grant it the 0640 renders)")
    return ok


def test_grafana_provisioning_dirs_are_traversable() -> bool:
    """Every grafana dir the role creates must be readable+traversable as 472:0."""
    body = _read(TASKS)
    if body is None:
        print("FAIL: grafana dirs traversable (tasks/main.yml unreadable)")
        return False
    declared = _directory_declarations(body)
    missing = [d for d in REQUIRED_GRAFANA_DIRS if f"{PROJECT_DIR}/{d}" not in declared]
    if missing:
        print(f"FAIL: grafana dirs traversable (never created: {missing})")
        return False
    bad = []
    for rel in REQUIRED_GRAFANA_DIRS:
        name, mode, owner, group = declared[f"{PROJECT_DIR}/{rel}"]
        bits = _mode_bits(mode)
        if bits is None:
            bad.append(f"{rel}: undecodable mode {mode!r} in task {name!r}")
            continue
        granted, why = _grants_access(bits, owner, group, need_exec=True)
        if not granted:
            bad.append(f"{rel}: not r-x for uid {GRAFANA_UID} gid 0 ({why})")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: the {len(REQUIRED_GRAFANA_DIRS)} grafana provisioning dirs are "
          f"r-x for uid {GRAFANA_UID}/gid 0 (problems={bad})")
    return ok


def test_grafana_delivered_files_are_readable() -> bool:
    """Every file the role puts under grafana/ must be readable as 472:0.

    An inventory over the DEST rather than a list of three names: the datasource
    provisioning, the dashboard provider and every dashboard JSON are all read
    by the same process, so a file a later task adds is checked by the fact that
    it is delivered there.
    """
    body = _read(TASKS)
    if body is None:
        print("FAIL: grafana delivered files readable (tasks/main.yml unreadable)")
        return False
    deliveries = _grafana_file_deliveries(body)
    if not deliveries:
        print("FAIL: grafana delivered files readable (no file is delivered under grafana/ at all)")
        return False
    bad = []
    for name, dest, mode, owner, group in deliveries:
        bits = _mode_bits(mode)
        if bits is None:
            bad.append(f"{dest}: undecodable mode {mode!r} in task {name!r}")
            continue
        granted, why = _grants_access(bits, owner, group, need_exec=False)
        if not granted:
            bad.append(f"{dest}: not readable by uid {GRAFANA_UID} gid 0 ({why})")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: all {len(deliveries)} files delivered under grafana/ are readable "
          f"by uid {GRAFANA_UID}/gid 0 (problems={bad})")
    return ok


def test_datasource_declares_an_explicit_uid() -> bool:
    """The provisioned datasource must pin its own uid.

    Without `uid:` Grafana generates one — measured `PBFA97CFB590B2093`, calibration
    row C1 — and a dashboard cannot reference a value that does not exist until the
    server has already started.
    """
    body = _read(DATASOURCE_TPL)
    if body is None:
        print("FAIL: datasource declares an explicit uid (template unreadable)")
        return False
    entries = _datasource_entries(body)
    if not entries:
        print("FAIL: datasource declares an explicit uid (no `datasources:` entries parsed)")
        return False
    bad = [f"{name!r}: uid={uid!r}" for name, uid in entries
           if not uid or "{" in uid or "$" in uid]
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: all {len(entries)} provisioned datasource(s) pin a literal uid "
          f"(problems={bad})")
    return ok


def test_datasource_uid_change_is_migrated() -> bool:
    """A pinned uid needs a `deleteDatasources:` entry, BY NAME, in the same org.

    THE ROW THAT WAS MISSING, and it is not a completeness quibble: without it
    the guard was rc=0 PASS on a tree that will not boot. Grafana provisioning
    matches an existing datasource BY NAME, so pinning `uid:` on a name the
    store already holds under a generated one is a MIGRATION, not an edit.
    Measured on grafana/grafana:13.1.0 against a store seeded with the file this
    repo actually shipped from a8c17db (`logs/red-step04a-migration-battery.log`):

        M2  the dirty store + the uid pin, no delete block   DID NOT START, exit 1
        M3  the dirty store + the delete block               HEALTHY, uid resolves 200
        M4  M3's store rebooted with the same file           HEALTHY  (idempotent)
        M5  a fresh store + the same file                    HEALTHY  (greenfield)

    M2's death is `Datasource provisioning error: data source not found`, the
    provisioning module failing and taking every dependent module with it, under
    `restart: unless-stopped` — the crash loop this wave exists to end.

    BOTH HALVES OF THE TIE ARE MEASURED, so neither is decoration: pointing the
    delete at `orgId: 2` (row M6) or at a different NAME (row M7) dies exactly
    the way M2 does. Hence name equality AND orgId equality, with an absent
    `orgId` on either side read as Grafana's default org 1.

    The reverse direction is checked too — a delete naming something the file
    does not re-create removes a datasource nothing puts back, which is the same
    outage arriving from the other side.
    """
    body = _read(DATASOURCE_TPL)
    if body is None:
        print("FAIL: uid pin is migrated (template unreadable)")
        return False
    provisioned = _provisioning_entries(body, "datasources")
    if not provisioned:
        print("FAIL: uid pin is migrated (no `datasources:` entries parsed)")
        return False
    deleted = _provisioning_entries(body, "deleteDatasources")
    bad = []
    delete_orgs = {}
    for entry in deleted:
        name = entry.get("name")
        if not name:
            bad.append(f"a deleteDatasources entry has no name: {entry}")
            continue
        delete_orgs[name] = (entry.get("orgId") or "1").strip()
    for entry in provisioned:
        name, uid = entry.get("name"), entry.get("uid")
        if not name:
            bad.append(f"a datasources entry has no name: {entry}")
            continue
        if not uid:
            continue  # test_datasource_declares_an_explicit_uid owns that failure
        org = (entry.get("orgId") or "1").strip()
        if name not in delete_orgs:
            bad.append(f"{name!r} pins uid {uid!r} but no deleteDatasources entry names it — "
                       "a store already holding that name under another uid refuses to start")
        elif delete_orgs[name] != org:
            bad.append(f"{name!r}: deleted from orgId {delete_orgs[name]!r} but provisioned "
                       f"into orgId {org!r} — the delete misses (battery row M6)")
    orphans = sorted(set(delete_orgs) - {e.get("name") for e in provisioned})
    if orphans:
        bad.append(f"deleteDatasources removes {orphans}, which nothing here re-creates")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: all {len(provisioned)} provisioned datasource(s) are deleted "
          f"by name first ({len(delete_orgs)} deleteDatasources entr(ies)) (problems={bad})")
    return ok


def test_provisioning_files_have_no_duplicate_key() -> bool:
    """Neither provisioning template may define a mapping key twice.

    THE ROUND-1 FAIL-OPEN, ONE KEY OVER: the guard was rc=0 PASS on a tree that
    will not boot. Grafana's YAML is v3-strict, so a duplicate key is not
    last-wins — the server exits 1 with `yaml: unmarshal errors: … mapping key
    "datasources" already defined` and `restart: unless-stopped` turns that into
    the crash loop this wave exists to end. Measured at four depths and in both
    files; see `_duplicate_mapping_keys` for the rows.

    Both templates are read, not just the datasource one: row K2 is the provider
    file dying the same way, and 4b/4c each add a delivery to that side.
    """
    bad = {}
    for tpl in (DATASOURCE_TPL, DASHBOARDS_TPL):
        body = _read(tpl)
        if body is None:
            bad[tpl.name] = ["unreadable"]
            continue
        found = _duplicate_mapping_keys(body)
        if found:
            bad[tpl.name] = found
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: no duplicate mapping key in the 2 provisioning "
          f"template(s) (problems={bad})")
    return ok


def test_delivered_dashboards_reference_the_provisioned_uid() -> bool:
    """THE CROSS-FILE ROW: the provisioned uid and every dashboard's refs agree.

    One side is `grafana-datasource.yml.j2`, the other is every JSON the role
    delivers into the mounted dashboards dir. A check that read either side
    alone would be green on the delivered defect — the uid was generated and the
    JSON said `Prometheus` — which is what makes reading both the point of this
    file rather than a nicety.

    Anti-vacuity, both ways: an empty inventory FAILS, a delivered dashboard that
    references no datasource at all FAILS, and a delivery with no `src:` FAILS
    rather than being skipped — so this cannot be satisfied by delivering
    nothing, by a dashboard whose panels query nowhere, or by inlining the JSON
    into the task file where no reader here can see it.

    Grafana's three BUILT-IN datasource uids are accepted and counted separately
    (see `GRAFANA_BUILTIN_DATASOURCE_UIDS`) rather than being required to appear
    in the provisioning file, which declares real datasources only. The count is
    printed so that "the refs all resolved" and "the refs were all built-ins"
    can never read the same on the gate's output.
    """
    ds_body, tasks_body = _read(DATASOURCE_TPL), _read(TASKS)
    if ds_body is None or tasks_body is None:
        print("FAIL: dashboard refs match the provisioned uid (a source file is unreadable)")
        return False
    provisioned = {uid for _, uid in _datasource_entries(ds_body) if uid}
    if not provisioned:
        print("FAIL: dashboard refs match the provisioned uid (provisioning declares no uid)")
        return False
    inventory = _delivered_dashboards(tasks_body)
    if not inventory:
        print("FAIL: dashboard refs match the provisioned uid (no dashboard is delivered)")
        return False
    bad = []
    total_refs = builtin_refs = 0
    for name, src, _dest, rendered in inventory:
        if src is None:
            bad.append(f"{name!r}: delivered with no `src:` — its JSON is inline, "
                       "so no uid reference in it can be read here")
            continue
        raw = _read(src)
        if raw is None:
            bad.append(f"{name!r}: src {src} "
                       f"{_unreadable(src, provisioned=True, rendered=rendered)}")
            continue
        try:
            doc = _grafana_provisionable_json(raw)
        except (json.JSONDecodeError, GrafanaUnprovisionableJSON) as exc:
            bad.append(f"{src.name}: not a dashboard the provisioner loads ({exc})")
            continue
        refs = _datasource_refs(doc)
        if not refs:
            bad.append(f"{src.name}: references no datasource at all")
            continue
        total_refs += len(refs)
        for where, uid, _kind in refs:
            if uid in GRAFANA_BUILTIN_DATASOURCE_UIDS:
                builtin_refs += 1
            elif uid not in provisioned:
                bad.append(f"{src.name}{where[1:]}: uid {uid!r} neither provisioned "
                           f"{sorted(provisioned)} nor built in")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: {total_refs} datasource reference(s) across "
          f"{len(inventory)} delivered dashboard(s) resolve to provisioned uid(s) "
          f"{sorted(provisioned)} ({builtin_refs} to a grafana built-in) (problems={bad})")
    return ok


def test_delivered_dashboard_datasource_types_agree_with_the_provisioned_uid() -> bool:
    """A carrier that names a provisioned uid AND declares a `type` must declare
    THAT uid's type.

    THE SAME LINE, READ THE OTHER WAY. The row above asks whether a carrier's
    `uid` resolves; this asks whether the `type` written beside it is the type
    provisioned AT that uid. `grafana-datasource.yml.j2` declares both at every
    uid it provisions, so the comparison is a cross-file one this file can make
    and nothing else does — and until it did, `{"type": "loki", "uid":
    "Prometheus"}` was a sentence no row in this file disagreed with.

    THE TYPE DECIDES NOTHING AT QUERY TIME, WHICH IS WHY THIS IS NOT COSMETIC —
    it is what makes the mismatch SILENT rather than self-punishing. Measured on
    grafana/grafana:13.1.0 through its own query endpoint, with a datasource
    whose URL is dead so the error names who was consulted
    (`logs/calibration-step05b-type-vs-uid-routing.py` R2-R5, 10/10): a query
    spelled `{"type": "loki", "uid": "Prom5b"}` reaches the PROMETHEUS
    datasource at that uid, and the reply is BYTE-IDENTICAL to the one the
    matching-type control gets. The uid routes; the type is believed. So a
    mismatched carrier still ships PromQL to Prometheus — while
    `test_delivered_dashboard_queries_are_readable` reads that same `type`,
    concludes the carrier holds no PromQL, and stops asking whether its query
    sits anywhere this file can read (measured as green before this row existed:
    probe N11 of `logs/critic-step04c-r11-probe.py`, and B1 of
    `logs/red-step05b-datasource-type.py`). The exemption is not widened to
    repair that — a declared non-prometheus type is still an exemption, and it
    has to be, or Grafana's own built-in annotation reddens (probe N10) — the
    two rows COMPOSE instead: the exemption may believe the type because this
    row refuses a type that disagrees with the uid beside it.

    WHAT THIS ROW DOES NOT ASK, and it is a bound rather than an oversight. A
    carrier naming one of Grafana's three BUILT-IN uids is not compared, because
    the provisioning file declares those nowhere — none of the three appears in
    the datasource list a provisioning file writes (calibration R9, the three
    themselves pinned by R7), so this repo holds no type to compare against. The
    id IS readable, but only off a RUNNING server, which a static file check at
    gate time has not got: on `/api/frontend/settings` that endpoint's own
    `type` reports the plugin CATEGORY `datasource` for all three while their
    `meta.id` differs, and for `-- Grafana --` that id is `grafana` — exactly
    the type probe N10's carrier writes (R8; the other two ids, `mixed` and
    `dashboard`, are measured on the server but against no dashboard here).
    Comparing them needs a constant transcribed from Grafana rather than read
    out of this repo, which is a different claim with a different failure mode
    (it goes stale on upgrade, in the loud direction), so it is
    `code-assist:plex-monitoring:guard:builtin-datasource-type-unpinned` and not
    a widening of this row. The mutation it does not see is named so a reader
    does not have to find it: `{"type": "loki", "uid": "-- Grafana --"}` on a
    target whose query is in an unknown key. The count of built-in carriers is
    printed, so "compared them all" and "skipped them all" cannot read alike.

    Anti-vacuity, and it is this row's own: ZERO comparisons FAILS. Stripping
    every `type` from every delivered carrier leaves the row with nothing to
    disagree with, and a strip is exactly what a mechanical edit does (B7); so
    is the truth source losing its own `type:` line, which is why a provisioned
    uid that declares no type is a problem printed here (B8) rather than a
    carrier silently skipped.
    """
    ds_body, tasks_body = _read(DATASOURCE_TPL), _read(TASKS)
    if ds_body is None or tasks_body is None:
        print("FAIL: declared datasource type(s) agree with the provisioned uid "
              "(a source file is unreadable)")
        return False
    provisioned = _datasource_types(ds_body)
    if not provisioned:
        print("FAIL: declared datasource type(s) agree with the provisioned uid "
              "(provisioning declares no uid)")
        return False
    inventory = _delivered_dashboards(tasks_body)
    if not inventory:
        print("FAIL: declared datasource type(s) agree with the provisioned uid "
              "(no dashboard is delivered)")
        return False
    bad = [f"provisioned uid {uid!r} declares no `type:` of its own, so a carrier "
           f"naming it has nothing to agree with"
           for uid, kind in sorted(provisioned.items()) if not kind]
    compared = builtin = untyped = elsewhere = 0
    per_dashboard = []
    for _name, src, _dest, _rendered in inventory:
        raw = _read(src) if src is not None else None
        if raw is None:
            continue
        try:
            doc = _grafana_provisionable_json(raw)
        except (json.JSONDecodeError, GrafanaUnprovisionableJSON):
            continue  # the row above names an unreadable delivery; two voices help nobody
        here = 0
        for where, uid, kind in _datasource_refs(doc):
            if kind is None:
                untyped += 1
                continue
            if uid in GRAFANA_BUILTIN_DATASOURCE_UIDS:
                builtin += 1
                continue
            if uid not in provisioned:
                elsewhere += 1
                continue
            if provisioned[uid] is None:
                continue  # already a problem above, and not this carrier's fault
            here += 1
            if kind != provisioned[uid]:
                bad.append(f"{src.name}{where[1:]}: declares type {kind!r} beside uid "
                           f"{uid!r}, which is provisioned as {provisioned[uid]!r} — the "
                           f"uid routes the query and the type is believed by "
                           f"`test_delivered_dashboard_queries_are_readable`, so this "
                           f"carrier is exempted from a query it still sends")
        compared += here
        per_dashboard.append(f"{src.name}: {here} compared")
    if not compared:
        bad.append("no delivered carrier declares a datasource type on a provisioned uid "
                   "— this row compares nothing, so it cannot be evidence of agreement")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: {compared} declared datasource type(s) across "
          f"{len(inventory)} delivered dashboard(s) agree with the type provisioned at "
          f"the uid they name ({ {u: k for u, k in sorted(provisioned.items())} }) "
          f"({builtin} on a grafana built-in, {untyped} carrier(s) declare no type, "
          f"{elsewhere} name no provisioned uid; {per_dashboard}) (problems={bad})")
    return ok


def _dashboard_sources_on_disk() -> set:
    """Every file in the role that IS a dashboard — by name OR by content.

    THE ON-DISK SIDE OF THE INVENTORY, and it used to be two filename globs
    alone. Nothing in this repo enforces the `dashboard` token, so the glob was a
    convention doing load-bearing work: measured on the real tree
    (`logs/review-step04b-r3-sibling-dir.log` G6/G7), a 4c-shaped
    `files/grafana-plex-health.json` with NO delivery task and `tasks/main.yml`
    unmutated is guard PASS 13/13, while the IDENTICAL BYTES renamed to carry the
    token are RED. The filename was the whole difference between a dashboard held
    to all thirteen checks and one held to none.

    The globs are KEPT and unioned with a content test, so nothing today's
    spelling catches is lost (`logs/rework-step04b-r5-subdir-and-keys-post.log`
    R8). A file is a dashboard by content when it parses to a mapping carrying a
    top-level `uid` and `title` — EXACTLY the keys
    `test_delivered_dashboards_parse_as_dashboards` demands on the delivered
    side, so the two directions of the inventory agree on what the word means.

    THE KEY SET WAS WIDER FOR ONE ROUND AND THE EXTRA KEY WAS WRONG. Round 4 also
    required `panels`/`schemaVersion` and justified it with a PAIR argument: a
    shape this cannot claim "cannot ship, only sit unwired", because the
    delivered-side parse check reddens it. That holds for the NO-UID shape and is
    FALSE for the other shape it excluded. Measured (same log, R6): a dashboard
    carrying `uid`+`title`+a real datasource ref and NO top-level
    `panels`/`schemaVersion`, DELIVERED, is guard GREEN 13/13 — it SHIPS. Its
    undelivered twin was invisible here (R7). Aligning the two sides on one key
    set is what closes that, and DEC-076 records the correction to DEC-075.

    WHERE IT LOOKS IS `rglob`, NOT `glob`, and that is not tidiness. `Path.glob`
    is not recursive, so every pattern here was pinned to the TOP LEVEL while the
    DELIVERED side has no such limit — `_delivered_dashboards` builds `root / src`
    and ansible's `src:` takes directory components. Measured (same log): an
    ordinary undelivered dashboard at `files/dashboards/…json` was guard PASS
    13/13 with `tasks/main.yml` unmutated (R1) while the IDENTICAL BYTES one
    directory UP were RED (R2) — the directory was the whole difference. That the
    subdirectory spelling is real ansible and not a straw man was asked of real
    ansible-core 2.21.1 through the role resolution path
    (`logs/review-step04b-r4-subdir-ansible.log`, 5/5): `copy:`/`template:` with
    `src: dashboards/x.json` lands, renders, and says nothing. Its delivered pair
    stays GREEN here (R4) and is held to the other twelve checks (R5).

    BOTH DIRECTIONS OF THE RULE ARE MEASURED:
      * what it newly FORBIDS is only a file that LOOKS like a dashboard — a
        non-dashboard JSON stays GREEN, in a subdirectory too (R9), and a
        `.json.j2` whose Jinja sits in a STRUCTURAL slot does not parse and is
        not claimed.
      * what it CLAIMS stops short of the provider, and by a MEASURED amount
        rather than a guessed one. Asked of real grafana/grafana:13.1.0 at the
        delivered root:root 0750/0640
        (`logs/rework-step04b-r4-content-keys-live.log`, 5/5): a dashboard with
        NO top-level `uid` IS loaded, silently, on a healthy server. So this key
        set is still strictly narrower than what the server will read, and an
        undelivered file of that shape is invisible HERE. Declared as a bound,
        and it is the bound the pair argument DOES cover: delivered, that shape
        is RED from the parse check, so it cannot ship — only sit unwired.

        It stays at `uid`+`title` rather than going wider: widening to `title`
        alone, or to "any JSON mapping", would claim files by the commonest keys
        in JSON and make every future non-dashboard JSON added to `files/` a
        guard failure with no correct fix.

    ONE MORE DECLARED BOUND, from the same log (R10): a bare `.j2` src with no
    `.json` in the name — `templates/grafana-plex-health.j2`, guard-GREEN when
    delivered to a `.json` dest — matches no pattern here, and `rglob` does not
    close it. Every template in this role is spelled `<name>.<ext>.j2`, so the
    pattern reads the repo's convention; a dashboard spelled otherwise and left
    undelivered is invisible to this check. Named so it is a known edge and not
    a discovery.
    """
    found = {p.resolve() for p in FILES.rglob("*dashboard*.json")}
    found |= {p.resolve() for p in TEMPLATES.rglob("*dashboard*.json.j2")}
    for path in _role_json_sources():
        raw = _read(path)
        if raw is None:
            continue                       # reported by `_undecodable_role_json`, not lost
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(doc, dict) and doc.get("uid") and doc.get("title"):
            found.add(path.resolve())
    return found


def _role_json_sources() -> list:
    """Every `.json` / `.json.j2` under the role's `files/` and `templates/`, sorted.

    The set the content test above scans, named once so the reader that CLASSIFIES
    them and the reader that reports the ones it cannot classify walk the same
    files rather than two hand-copied glob lists.
    """
    out = []
    for root in (FILES, TEMPLATES):
        out += sorted(list(root.rglob("*.json")) + list(root.rglob("*.json.j2")))
    return out


def _undecodable_role_json() -> list:
    """The role's JSON sources that cannot be decoded — the discovery THIRD STATE.

    NOT A SKIP, AND THE DIFFERENCE IS A MEASURED rc. `_dashboard_sources_on_disk`
    answers "is this file a dashboard", and for a file it cannot decode the honest
    answer is neither yes nor no. Continuing past it made it a NO, and that is the
    one direction this side of the inventory cannot afford: a file it silently
    drops is a file no other row reads either, because every other reader is keyed
    on a DELIVERY. Measured on a tempdir copy (`logs/critic-579d-bad-byte-position`
    P4, reproduced by `red-579d-r2-position-and-discovery.py` C2): an UNDELIVERED
    `files/starter.json` carrying one `0xff`, whose name misses the `*dashboard*`
    glob, took the gate from a traceback straight to `PASS: 21/21` rc=0 once the
    decode was caught — a file the guard had no verdict on, scored as if it were
    not there. It is mem-1785563013-32c7 with the other sign: a DISCOVERY reader
    must stay WIDER than the delivery ones, because refusing a broken file here
    HIDES it instead of reporting it.

    THE DECLARED BOUND: this reddens on any `.json`/`.json.j2` under the role that
    is not valid UTF-8, dashboard or not. RFC 8259 makes UTF-8 the encoding of
    JSON exchanged between systems, and the row can name the file and the byte —
    which is strictly more than the silence it replaces. A file that is genuinely
    not JSON belongs under another extension.
    """
    return [p for p in _role_json_sources() if _read(p) is None]


def test_dashboard_delivery_inventory_is_complete() -> bool:
    """Every dashboard JSON in the role ships, and everything shipped exists.

    The other direction of the inventory. A JSON added to `files/` and never
    delivered is a dashboard nobody sees and, worse, a file the cross-file uid
    check never reads — so authoring one without its delivery task must redden
    HERE, in the wave where 4b and 4c each add exactly that pair.

    WHAT COUNTS AS "a dashboard JSON in the role" is `_dashboard_sources_on_disk`,
    which reads content and not only filenames — the promise above was keyed on a
    naming convention nothing enforces until round 4 measured it.

    This is also the check that answers for a dashboard delivered OUTSIDE the
    dashboards tree, which is not obvious from its name: `_delivered_dashboards`
    is keyed on the dest, so a delivery one directory OVER is not in the delivered
    set at all, and the file it copies is therefore an ORPHAN here. Measured
    (`logs/rework-step04b-r4-inventory-content-post.log` W1) rather than assumed,
    because `test_dashboards_are_delivered_where_grafana_looks` used to claim it.

    AND IT IS THE ROW THAT REPORTS A JSON SOURCE NOTHING CAN DECODE, for the same
    reason it is the row that reports an undelivered one: it is the only reader
    here not keyed on a delivery, so a file it drops is a file the gate has no
    verdict on at all (`_undecodable_role_json`, and `red-579d-r2-…` C2/C3).
    """
    body = _read(TASKS)
    if body is None:
        print("FAIL: dashboard delivery inventory complete (tasks/main.yml unreadable)")
        return False
    inventory = _delivered_dashboards(body)
    delivered = {src.resolve() for _, src, _d, _r in inventory if src is not None}
    srcless = sorted(name for name, src, _d, _r in inventory if src is None)
    on_disk = _dashboard_sources_on_disk()
    undelivered = sorted(str(p.relative_to(REPO_ROOT)) for p in on_disk - delivered)
    missing_src = sorted(str(p) for p in delivered if not p.is_file())
    # NO `provisioned=True` HERE, and that is the whole of this row's claim: it
    # walks every role JSON, dashboard or not, delivered or not, so it does not
    # know that any engine reads the file it is naming. A delivered one that
    # cannot be decoded is named by the five delivery-side rows WITH the
    # provisioner sentence in the same run, so nothing is lost by withholding it
    # here (`red-579d-r3-escape-slot-and-subject.py` PART G).
    unreadable = [f"{p.relative_to(REPO_ROOT)}: {_unreadable(p)}"
                  for p in _undecodable_role_json()]
    ok = (not undelivered and not missing_src and not srcless and not unreadable
          and bool(delivered))
    print(f"{'OK' if ok else 'FAIL'}: {len(delivered)} dashboard file(s) delivered, none orphaned "
          f"(undelivered={undelivered} missing_src={missing_src} inline={srcless} "
          f"unreadable={unreadable})")
    return ok


# The `uid` a delivered dashboard must carry, MEASURED rather than inherited.
#
# THIS IS THE SAVE LAYER, AND IT IS NOT THE PARSE LAYER. `_grafana_provisionable_json`
# answers a JSON question — the bytes Go's `encoding/json` refuses to unmarshal at all
# — and every one of its callers wraps it in an `except` about an UNREADABLE delivery.
# A 41-character uid is perfect JSON. It is refused one step later, by the provisioner's
# own save-time validation, on the SAME `failed to save dashboard` log line and with the
# same 404 at `/api/dashboards/uid/<uid>`. So the rule lives HERE, in the row that reads
# the field, beside the `uid`/`title` truthiness test whose `title` half already catches
# this class's other member (an empty title is 404 at the engine and RED here).
#
# MEASURED ON THE PINNED `grafana/grafana:13.1.0` — the tag `defaults/main.yml` pins —
# with the repo's own file-provider shape, asked over Grafana's own HTTP API, one
# delivered file per candidate, 121 of them in one provisioning run
# (`logs/calibration-step05d-rework-r9-uid-charset.py` / `.log`, 31/31):
#
#   * THE CHARSET IS EXACTLY `[A-Za-z0-9_-]`. Swept over every printable ASCII
#     character plus tab/CR/LF and a unicode sample: 64 accepted, 40 refused, and the
#     accepted set is that class with nothing extra and nothing missing (row A1). `.`
#     and `/` and a space are refused — `uid contains illegal characters` — and so is
#     every non-ASCII candidate (A4), which is why this is not a "printable" test.
#   * THE LENGTH STEPS AT 40. 1, 2, 39 and 40 characters provision; 41, 42, 64 and 128
#     do not — `uid too long, max 40 characters` (rows B1…B128).
#   * AND THE TWO ARE ORDERED, WHICH 121 SINGLE-DEFECT FILES COULD NOT SAY. Every candidate
#     above carries ONE defect, so the sweep prices each rule and orders neither against the
#     other. A uid that breaks BOTH is refused on the CHARSET — `uid contains illegal
#     characters` for `"u"*41 + " x"` and for `"u v" + "u"*40` alike, one delivered file each
#     in the run that also names `uid too long` for a legal 41-character uid
#     (`logs/red-579d-r8-title-before-uid.py` PART A, E-uid_both_tail/head/agree). That is
#     the order `_grafana_short_uid_defect` asks them in, because `_unreadable` quotes the
#     rule at an operator and a document has only one rule the engine stopped on.
#   * AND BOTH OF THEM SIT BELOW A **TRIM**, so the bullet above is a claim about an
#     INTERIOR illegal character and about nothing else. Both of its carriers put the space
#     inside the string — 42nd of 43 and 2nd of 43 — and at the TRUE ends the trim runs
#     first and the answer flips to `uid too long` for the same 42-character strings
#     (`logs/red-579d-r9-uid-trim-class.py` D4). See `GRAFANA_SHORT_UID_TRIM` below.
#   * AND A NON-STRING `uid` IS A DIFFERENT OUTCOME, WHICH IS WHY THE REASON SPLITS.
#     `42`, `4.5`, `true`, `[]` and `{}` are NOT refused: Grafana generates a fresh
#     UUID and SAVES the dashboard under it (row C2 — measured addresses like
#     `9c84bd86-7f51-46ed-9b0c-3dff53624948`). The file is not missing, it is at an
#     address no line in this repo can name, and the cross-file `uid` row next door is
#     comparing a number the store never held. `42` as a STRING is an ordinary legal
#     uid and provisions (C1), so the test is on the TYPE and not on the spelling.
#
# The accept side is held by `logs/red-step05d-rework-r9.py` rows E1…E6 — the uid as
# delivered, both length edges, an all-digit string, and upper case — because a rule
# that refused a working dashboard is the failure this file has already paid for.
GRAFANA_SHORT_UID_CHARS = re.compile(r"\A[A-Za-z0-9_-]+\Z")
GRAFANA_SHORT_UID_MAX = 40

# THE CLASS THE ENGINE TRIMS OFF A `uid` BEFORE EITHER RULE ABOVE, AND IT IS THE TITLE'S
# CLASS MINUS U+FEFF.
#
# Both rules above are asked on what SURVIVES this trim, and the dashboard is SAVED under
# the trimmed uid. So a delivered uid carrying one of these at either end is a dashboard the
# provisioner serves, and calling it `uid contains illegal characters` was a false refusal on
# 28 of 38 candidates — the failure class the block above says this file pays to avoid, in
# the direction that reddens `just test` over a dashboard that works.
#
# MEASURED AT BOTH ENDS, ONE DELIVERED FILE PER CANDIDATE, THE STORED uid READ BACK OVER
# GRAFANA'S HTTP API, AND EVERY MEMBER CARRIED BY A RUN THAT NAMES IT:
#
#   * 13 of the 25 in `logs/critic-579d-r8-uid-trim-class.py` / `.log` (26/27, 38
#     candidates, each on its own base so no trimmed uid can collide with another's — B0
#     asserts 0 duplicate-uid warnings), and
#   * the other 12 — U+2001…U+200A, U+2029, U+205F — in
#     `logs/red-579d-r9-uid-trim-class.py` / `.log` (PART C, 41 candidates), which that
#     review declared explicitly NOT carried. The two runs answer the same for U+2000 and
#     U+3000 (C-bridge), which is what makes them one measurement and not two.
#
# U+FEFF IS THE WHOLE DIFFERENCE FROM `GRAFANA_TITLE_TRIM`, measured on both sides: the
# title's trim EATS it (F3 there) and a uid carrying it is REFUSED at both ends, `uid
# contains illegal characters` (r8 C-bom, r9 C-not-title). U+200B is in NEITHER class and is
# refused (C-zwsp). Two fields, two classes, two constants.
#
# AND THE TRIM IS ABOVE BOTH RULES, NOT BETWEEN THEM. A 41-character uid whose 41st is a
# class member is served under the 40 that survive (r8 D3, r9 D5-length-after-trim), and one
# that trims EMPTY is not refused at all: the engine generates a uuid and saves the dashboard
# at an address nothing in this repo can name — the same outcome as a non-string uid
# (calibration C2), measured at `allem` in the r9 run. The predicate names that case for the
# same reason it names C2, and `_grafana_stored_uid` below returns None for both.
#
# It is spelled as codepoints and NOT as literal characters, for the reason
# `GRAFANA_TITLE_TRIM` gives at length: every member is invisible in a source file and two of
# them cut this file in two for any reader that tokenises lines.
GRAFANA_SHORT_UID_TRIM = "".join(chr(c) for c in (
    [0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20, 0x85, 0xA0, 0x1680]    # Go's Latin-1 cases, OGHAM
    + list(range(0x2000, 0x200B))                               # EN QUAD ... HAIR SPACE
    + [0x2028, 0x2029, 0x202F, 0x205F, 0x3000]                  # LS, PS, NNBSP, MMSP, IDEO
))


def _grafana_stored_uid(uid) -> str | None:
    """The `uid` the provisioner SAVES this dashboard under, or None when it invents one.

    ONE FUNCTION BECAUSE TWO ROWS ASK THE SAME QUESTION, and they were answering it
    differently. `_grafana_short_uid_defect` needs it to ask the charset and the length of
    the string the engine really validates; `test_delivered_dashboards_have_distinct_uids`
    needs it because the STORE keys on this value, so two delivered dashboards whose uids
    differ only by a member of the trim class are one dashboard at the engine and the second
    quietly overwrites the first.

    None means "the engine picks the address, not this file": a non-string uid (calibration
    C2) and a uid that trims empty (`red-579d-r9-uid-trim-class` PART A `allem`) both get a
    freshly generated uuid. Neither is an address any line in this repo can name — which is
    why the predicate below reports both — and no dashboard can be LOST to one.

    THAT IS A STATEMENT ABOUT THE ADDRESS AND NOT ABOUT THE DEDUPE, and callers have read it
    as both. Grafana's duplicate check reads the uid AS DELIVERED, so two files carrying ONE
    empty-trimming spelling are a duplicate to it — warning, and the provider's writes
    disabled — while both are served (`red-579d-r11.py` PART A `ra`, and `rc` for the
    distinct-spelling half that is silent). A caller that needs the dedupe's key must group
    on the delivered string and NOT on this function's answer.
    """
    if not isinstance(uid, str):
        return None
    return uid.strip(GRAFANA_SHORT_UID_TRIM) or None


def _grafana_short_uid_defect(uid) -> str | None:
    """Why the provisioner will not save a dashboard under this `uid`, or None.

    Separate from `_grafana_provisionable_json` on purpose: that one raises, because a
    file it refuses has no document to go on reading, while this is one more predicate
    over a document already in hand — the shape the `title` half of the same class
    already has here.

    THE TRIM IS ASKED FIRST, and it is asked on the string this file delivers rather than
    on the one the engine keeps. Everything below runs on `_grafana_stored_uid(uid)`: the
    provisioner strips `GRAFANA_SHORT_UID_TRIM` off both ends before either rule and saves
    the dashboard under what is left, so a uid with a trailing space is a dashboard the
    engine SERVES. Asking the charset of the delivered string reddened `just test` on 28 of
    38 candidates the store held (`logs/critic-579d-r8-uid-trim-class.py` D1) — every
    earlier finding in this thread was a wrong REASON on a refused document, and that one
    was a wrong VERDICT on a served one.

    THEN THE CHARSET, THEN THE LENGTH, FOR AN ILLEGAL CHARACTER THE TRIM CANNOT REACH.
    A caller that only reports WHETHER the uid is refused cannot tell the two apart, but
    `_unreadable` quotes the engine's own rule at an operator, so a uid that breaks both
    has to name the one the engine stopped on. The calibration that priced this class
    delivered each defect ALONE (`…-r9-uid-charset.py`, 121 files), which orders neither
    against the other; the round-7 review flagged the gap and declined to guess it.
    Carried (`logs/red-579d-r8-title-before-uid.py` PART A/E, one delivered file per
    carrier in ONE provisioning run on the pinned `grafana/grafana:13.1.0`, container log
    kept): a 43-character uid carrying a space is `uid contains illegal characters`, while
    the same run's 41-character legal uid IS `uid too long, max 40 characters`, which is
    what makes the length rule's silence on the other a measurement.

    AND THAT PAIR SAYS NOTHING ABOUT AN ILLEGAL CHARACTER AT AN END — which is what the
    sentence that stood here claimed. Both carriers are INTERIOR: `"u"*41 + " x"` puts the
    space 42nd of 43 and `"u v" + "u"*40` puts it 2nd, so "at the END and at the FRONT
    alike" was a property of two interior positions and not of the ends it named. At the
    true ends the trim above runs first and the answer FLIPS — `"u"*41 + " "` and
    `" " + "u"*41` are both `uid too long, max 40 characters` at the engine and here
    (`logs/red-579d-r9-uid-trim-class.py` D4, one delivered file each in the run that names
    the CHARSET for the same character in the middle, B2/B3). A claim about a POSITION
    needs a carrier at that position (mem-1785593456-9d15).
    """
    if not isinstance(uid, str):
        return (f"uid {uid!r} is {type(uid).__name__}, not a string — the provisioner does not "
                "refuse it, it GENERATES a uuid and saves the dashboard at an address nothing "
                "in this repo can name (calibration C2)")
    saved = _grafana_stored_uid(uid)
    if saved is None:
        return (f"uid {uid!r} is only the engine's trim class — it does not refuse it, it "
                "GENERATES a uuid and saves the dashboard at an address nothing in this repo "
                "can name (red-579d-r9-uid-trim-class `allem`, stored under a uuid)")
    if not GRAFANA_SHORT_UID_CHARS.match(saved):
        illegal = sorted({c for c in saved if not GRAFANA_SHORT_UID_CHARS.match(c)})
        return (f"uid {uid!r} carries {[hex(ord(c)) for c in illegal]}, outside [A-Za-z0-9_-] — "
                "the provisioner refuses to save it: `uid contains illegal characters`, 404 "
                "(calibration A1)")
    if len(saved) > GRAFANA_SHORT_UID_MAX:
        return (f"uid {uid[:16]!r}… is {len(saved)} characters after the engine's trim — the "
                f"provisioner refuses to save it: `uid too long, max {GRAFANA_SHORT_UID_MAX} "
                "characters`, 404 (calibration B41)")
    return None


# The `title` a delivered dashboard must carry — THE SAME SAVE LAYER, THE OTHER FIELD.
#
# `not doc.get("title")` below is PYTHON's idea of an absent title, which is what the
# `uid` half was before the rule above it. Fourteen titles Python calls truthy are 404 at
# the provisioner on the SAME `failed to save dashboard` line, so the row's own sentence
# — "a uid + title THE PROVISIONER SAVES" — was true of `""` and of nothing else.
#
# MEASURED ON THE PINNED `grafana/grafana:13.1.0`, one delivered file per candidate, in
# two runs of 94 and 535 files (`logs/calibration-step05d-rework-r10-title.py` 88/94, six
# deliberate REDs; `-title-class.py` 72/72). Three of the four bounds below CONTRADICT the
# rule the r9 review's own sentence produces, which is why none of them is inherited:
#
#   * THE TYPE. A non-string `title` is not a type error at the engine: simplejson's
#     `MustString()` yields `""`, so `42`, `4.5`, `true`, `["Homelab"]` and
#     `{"text": …}` all land on `Dashboard title cannot be empty` (C1/C2). `"42"` as a
#     STRING is an ordinary title and saves (C3) — the test is on the type, never the
#     spelling. This is the opposite of the `uid` rule one step up, where a non-string is
#     SAVED under a generated uuid; two fields, one layer, two outcomes.
#
#   * THE TRIM'S CLASS IS Go's `unicode.White_Space` PLUS U+FEFF — 26 codepoints, and
#     PYTHON'S `str.strip()` IS NEITHER A SUPERSET NOR A SUBSET OF IT. Every codepoint in
#     Unicode whose category is Cc/Cf/Zs/Zl/Zp (254 of them) was delivered alone as a
#     title, and again wrapped around a real one to prove the mechanism is a trim and not
#     a filter (F1/G1/G2). The two sets CROSS:
#         U+001C U+001D U+001E U+001F  python strips them, THE ENGINE SAVES THEM (F2)
#                                      → `not title.strip()` is a FALSE REFUSAL, four ways
#         U+FEFF                       python keeps it, THE ENGINE TRIMS IT (F3)
#                                      → `not title.strip()` is a FAIL-OPEN, one way
#     and 228 other invisible codepoints — U+200B, U+200D, U+00AD, U+2060 among them —
#     save (F5), so the class is the White_Space property and not "shows nothing".
#
#   * THE LENGTH IS COUNTED IN UTF-8 BYTES, whatever `Dashboard title cannot contain more
#     than 5 000 characters` says: it is `len()` on a Go string. 5000 ASCII saves; 2500
#     two-byte characters (5000 bytes) save and 2501 (5002 bytes) do not; 1666 three-byte
#     save and 1667 do not; 1250 four-byte save and 1251 do not (H1/H2/H3). So
#     `len(title) > 5000` in Python is a false accept on every multi-byte title between
#     5001 bytes and 5000 characters.
#
#   * AND THE COUNT IS TAKEN AFTER THE TRIM (H4): 5080 delivered bytes save when 5000 of
#     them survive it, and a padded 5002 does not.
#
# The accept side is held by `logs/red-step05d-rework-r10.py` rows E1…E13 — the delivered
# titles, an em dash, non-ASCII, a padded title, both length edges, and the four
# information separators a `strip()` rule would have refused.
# Spelled as codepoints and NOT as literal characters. Every member of this set is
# invisible in a source file; four of them are invisible in a way `str.strip()`
# disagrees about; and two of them (U+2028, U+2029) are line breaks to
# `str.splitlines()` — writing them literally would cut this very file in two for
# any reader that tokenises lines the way `_block_scalar` does (mem-1785550227-6d8a).
GRAFANA_TITLE_TRIM = "".join(chr(c) for c in (
    [0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20, 0x85, 0xA0, 0x1680]    # Go's Latin-1 cases, OGHAM
    + list(range(0x2000, 0x200B))                               # EN QUAD ... HAIR SPACE
    + [0x2028, 0x2029, 0x202F, 0x205F, 0x3000]                  # LS, PS, NNBSP, MMSP, IDEO
    + [0xFEFF]                                                  # the one python KEEPS (F3)
))
GRAFANA_TITLE_MAX_BYTES = 5000

# And the NINTH KEY OF THE SAME CARRIER, found by asking the other eight top-level keys of
# a delivered dashboard the same question rather than only the one the review named. The
# delivered files carry exactly ten: annotations, editable, panels, schemaVersion, tags,
# templating, time, title, uid, version. Given the most refusable value each one's type
# admits, NINE of the ten save — a non-object `time`/`annotations`/`templating`, a
# `panels` OBJECT, a string `schemaVersion`/`editable`, a 10^12 `version` (calibration
# PART E, and r8's own measurements for `id` and nesting). `tags` does not:
#
#     a `tags` member longer than 50 UTF-8 BYTES is `dashboard tag too long, max 50
#     characters`, 404, and it refuses the WHOLE FILE — one over-long tag among legal
#     ones and the dashboard never appears (I1/I2/I3).
#
# Its accept side is wide and is measured, not assumed: 200 tags, duplicates, an empty
# tag, a blank tag, a `tags` that is not a list at all, and non-string members all save,
# and a non-string member is silently DROPPED rather than refused (I4/I5) — so only a
# string member can carry the defect, and the rule is length alone.
GRAFANA_TAG_MAX_BYTES = 50

# AND THE STRING THOSE TWO BYTE COUNTS ARE TAKEN ON IS THE STRING **GO** DECODED, WHICH
# IS NOT ALWAYS THE STRING `json.loads` HANDS BACK.
#
# A delivered `.json` carries a LONE SURROGATE in pure ASCII: `"title": "A\ud800B"` is
# an ordinary escape on disk and `json.loads` yields the unpaired code point U+D800.
# Python cannot encode that — `str.encode("utf-8")` RAISES `UnicodeEncodeError` — and Go's
# `encoding/json` merely REPLACES it with U+FFFD and saves the dashboard. So the two
# `len(….encode("utf-8"))` calls below were not a wrong verdict on those files, they were
# NO verdict: the raise landed while row 11 of 21 was being evaluated, ten rows printed,
# the eleventh never ran, and this file's own summary line was never printed at all — a
# stack trace where four other harnesses look for a sentence (r10 review F1,
# `logs/critic-step05d-r10-surrogate-title.py` 34/37, `-surrogate-collateral.py` 14/14).
#
# MEASURED ON THE PINNED `grafana/grafana:13.1.0`, one delivered file per case in ONE
# provisioning run, read back over Grafana's own HTTP API with the STORED title recorded
# (`logs/calibration-step05d-rework-r11-surrogate.py` / `.log`, 38/38):
#
#   * THE REPLACEMENT IS PER CODEPOINT, AND U+FFFD IS THREE UTF-8 BYTES. `A\ud800B` is
#     stored `'A�B'` (C1) and two adjacent lone surrogates are stored as TWO U+FFFDs
#     (C2), so N of them cost 3N: 4997 ASCII + one saves at 5000 and 4998 + one is refused
#     at 5001, 4985 + FIVE saves and 4986 + five does not (B1/B3).
#   * BOTH FIELDS, BOTH DIRECTIONS. The same arithmetic at the OTHER field: a tag of 47
#     characters plus one surrogate is 50 bytes and saves; 48 plus one is 51 and takes the
#     WHOLE file down (B5), with 47 ASCII as the control (B6).
#   * IT IS ABOVE THE TRIM, AND THE TRIM DOES NOT MOVE. Neither a surrogate nor U+FFFD is
#     in `GRAFANA_TITLE_TRIM`, so a title that is ONLY a lone surrogate is stored `'�'`
#     and SAVES (C3), padded or wrapped in U+00A0/U+3000 it is trimmed AROUND the
#     replacement and still saves (C4/C5). No title changes its EMPTY verdict here; only
#     a length can move.
#   * AND A TITLE ALREADY CARRYING U+FFFD IS LEGAL TODAY AND STAYS SO (B4) — 4997 + U+FFFD
#     saves and 4998 + U+FFFD does not, exactly as its surrogate twin does, so modelling
#     the replacement cannot invent a defect.
#
# THE CLASS IS THE UNPAIRED SURROGATE AND NOT ADJACENCY, which my own first case list got
# wrong until the engine said so: a HIGH escape followed immediately by a LOW one is a
# PAIR — `"A𐀀B"` is stored `'A\U00010000B'` (C2b) — and `json.loads` joins it
# the same way, so a pair never reaches this function as surrogates at all. That is why
# the substitution below is written per code point rather than as a pass over pairs, and
# why `logs/red-step05d-rework-r11.py` E1/E2 hold the astral accept side.
_GRAFANA_LONE_SURROGATE = re.compile("[\ud800-\udfff]")


def _grafana_saved_text(text: str) -> str:
    """`text` as Go's `encoding/json` decoded it — every unpaired surrogate is U+FFFD.

    The one place this file has to speak Go's decoder rather than Python's, and it is
    deliberately NOT in the shared loader: a surrogate anywhere else in a delivered file
    is not refused by the engine and carries no rule, so replacing it there would change
    what every other row compares with nothing measured behind the change. Here it is
    load-bearing twice, because a BYTE COUNT is the one question whose answer differs.
    """
    return _GRAFANA_LONE_SURROGATE.sub("�", text)


def _grafana_saved_bytes(raw: bytes) -> str:
    """`raw` as Go's `encoding/json` decoded it — ONE U+FFFD per INVALID BYTE.

    The twin of `_grafana_saved_text` ONE LAYER DOWN: that one models what Go does with
    an unpaired surrogate ESCAPE, in a file Python can decode; this one models what it
    does with a RAW invalid byte, in a file Python cannot. `_unreadable` needs it to be
    able to ask the save-layer predicates below anything at all about such a file — the
    parse-layer classifier says only whether the engine substitutes or refuses, and a
    file it SUBSTITUTES then meets these rules with the substitution already in it.

    PYTHON'S OWN `errors="replace"` IS NOT THIS RULE, AND THE DIFFERENCE IS MEASURED
    RATHER THAN REASONED. Python substitutes one U+FFFD per MAXIMAL SUBPART (Unicode's
    recommendation, so a truncated prefix costs ONE); Go's `utf8.DecodeRune` returns
    `RuneError` with size 1 for every invalid encoding, so each byte costs its own.
    Measured on the pinned `grafana/grafana:13.1.0`, six sequences as one delivered file
    each in ONE provisioning run, the STORED title read back over the HTTP API with the
    anti-vacuity pair in that same run (`logs/red-579d-r5-save-layer-and-subject.py`
    PART C, 6/6):

        ed a0 80 -> 3      c0 80 -> 2      ff -> 1      c3 -> 1     both rules agree
        e2 82    -> 2      f0 9f -> 2                                python's rule: 1

    So `errors="replace"` is right for four of the six and wrong for both TRUNCATED
    prefixes. That is inert for the uid CHARACTER CLASS and load-bearing for both BYTE
    COUNTS — a 46-character tag plus a truncated `e2 82` is 52 bytes to the engine and
    49 to Python, one side of the 50 bound each (PART C-verdict, same run). This is a
    guard whose whole subject is "the string Python decoded is not the string Go
    decoded", so it does not get to use the wrong decoder at the one site that names it.

    It is NOT `_read`'s policy and does not become one: DEC-150 and DEC-167(iii) refused
    a loader-wide `errors=`, where every other row would compare a title that is not on
    disk. The substitution lives inside the REPORTING function, on bytes no other row
    holds, and the identity on any file that decodes at all.
    """
    out, start = [], 0
    while True:
        try:
            out.append(raw[start:].decode("utf-8"))
        except UnicodeDecodeError as exc:
            out.append(raw[start:start + exc.start].decode("utf-8"))
            # `exc.end - exc.start` is python's maximal subpart, which is exactly the
            # number of BYTES Go hands its own U+FFFD to, one at a time.
            out.append("�" * (exc.end - exc.start))
            start += exc.end
        else:
            return "".join(out)


# The top-level keys whose save-layer behaviour has been MEASURED on the pinned image.
# Not a refusal — a new Grafana release adds dashboard fields, and reddening for an inert
# one is the false refusal this file pays to avoid everywhere else — but a key outside it
# is a key nobody has asked, and the next reader is told so on the gate's own output.
GRAFANA_DASHBOARD_KEYS_PRICED = frozenset({
    "annotations", "editable", "id", "panels", "schemaVersion", "tags", "templating",
    "time", "title", "uid", "version",
})


def _grafana_dashboard_title(title) -> str:
    """The `title` GO holds for this value — `""` for anything that is not a string.

    THE LOAD LAYER'S OWN QUESTION, AND IT IS NOT THE SAME AS `_grafana_title_defect`'s.
    Grafana builds the dashboard from `simplejson` before any save-time validation runs,
    so a `title` that is absent, `null`, a number, `true`, a list or an object all arrive
    as `MustString()`'s `""` — and so does the empty string itself. The provisioner then
    refuses the file at the LOAD, on `failed to load dashboard from`, quoting the very
    same `Dashboard title cannot be empty` that a title empty only AFTER the trim quotes
    one layer later on `failed to save dashboard`. Measured on the pinned
    `grafana/grafana:13.1.0`, one delivered file per spelling in ONE provisioning run,
    container log kept, anti-vacuity in that same run
    (`logs/red-579d-r6-rule-to-log-line.py` PART A):

        absent  LOAD      null  LOAD      42  LOAD      ""  LOAD      "   "  SAVE

    SO THE DISCRIMINATOR IS NOT `isinstance`. The empty string is a `str` and lands on
    the LOAD line with the other three; a whitespace-only title is a `str` and does not.
    Text cannot separate them either — the two classes quote one error between them.
    `_grafana_saved_text` is applied for the reason it is applied everywhere else here:
    the string Go holds is not the string Python decoded, and a title that is ONLY a
    lone surrogate escape is U+FFFD to the engine and therefore NOT empty at this layer.

    The trim and the byte count stay where they were, in `_grafana_title_defect`, which
    keeps the `str | None` its own row compares. This function answers a different
    question for one caller: WHICH LINE the operator greps for.
    """
    return _grafana_saved_text(title) if isinstance(title, str) else ""


def _grafana_title_defect(title) -> str | None:
    """Why the provisioner will not save a dashboard under this `title`, or None.

    Beside `_grafana_short_uid_defect` and for the same reason: one more predicate over a
    document already in hand, at the layer that validates on SAVE rather than at the parse.

    THE TRIM AND THE COUNT ARE BOTH TAKEN ON `_grafana_saved_text(title)`, because the
    string the provisioner validates is the one GO decoded and Python's differs on exactly
    one class — the unpaired surrogate, which Go replaces with U+FFFD and `str.encode`
    refuses to encode at all. See the block above it; the trim verdict cannot move and
    only the byte count can.
    """
    if not isinstance(title, str):
        return (f"title {title!r} is {type(title).__name__}, not a string — Grafana's "
                "`MustString()` yields \"\", so the provisioner refuses to save it: "
                "`Dashboard title cannot be empty`, 404 (calibration C1/C2)")
    saved = _grafana_saved_text(title)
    trimmed = saved.strip(GRAFANA_TITLE_TRIM)
    if not trimmed:
        return (f"title {title!r} is empty after the ENGINE's trim "
                f"({[hex(ord(c)) for c in title[:8]]}, Go's unicode.White_Space plus "
                "U+FEFF) — the provisioner refuses to save it: `Dashboard title cannot be "
                "empty`, 404 (calibration F1/G1)")
    size = len(trimmed.encode("utf-8"))
    if size > GRAFANA_TITLE_MAX_BYTES:
        return (f"title {trimmed[:16]!r}… is {size} UTF-8 BYTES ({len(trimmed)} characters) "
                "— the provisioner refuses to save it: `Dashboard title cannot contain more "
                f"than 5 000 characters`, 404; the unit is the byte (calibration H1/H3)")
    return None


def _grafana_tags_defect(tags) -> str | None:
    """Why the provisioner will not save a dashboard carrying these `tags`, or None.

    Deliberately silent on everything the engine tolerates: a `tags` that is not a list is
    ignored by the engine and so is a non-string member (calibration I4/I5), and refusing
    either here would be a refusal the delivery path does not make.

    The 50 is counted on `_grafana_saved_text(tag)` for the reason the `title` rule counts
    on it: a 48-character tag plus one lone surrogate is 51 bytes to the engine and takes
    the whole file down (r11 calibration B5), and it is unencodable to Python.
    """
    if not isinstance(tags, list):
        return None
    for tag in tags:
        if not isinstance(tag, str):
            continue
        saved = _grafana_saved_text(tag)
        size = len(saved.encode("utf-8"))
        if size > GRAFANA_TAG_MAX_BYTES:
            return (f"tag {saved[:16]!r}… is {size} UTF-8 BYTES ({len(saved)} characters) — the "
                    "provisioner refuses to save the WHOLE dashboard: `dashboard tag too "
                    "long, max 50 characters`, 404 (calibration I1/I2/I3)")
    return None


def test_delivered_dashboards_parse_as_dashboards() -> bool:
    """Each delivered JSON must parse and carry a uid + title THE PROVISIONER SAVES.

    Grafana's file provisioner reads these at start; a malformed one is a
    dashboard that never appears. The dashboard's OWN `uid` is read here rather
    than in the cross-file check on purpose — `homelab-overview` is a top-level
    `uid` key that has nothing to do with a datasource reference, and keeping
    the two apart is what stops either check from answering for the other.

    "CARRIES A uid" IS TWO CLAIMS AND THE ROW USED TO MAKE ONE. A file can be
    readable JSON, carry a non-empty `uid`, and still never become a dashboard:
    the provisioner validates the uid when it SAVES, one step after the parse
    `_grafana_provisionable_json` models, and refuses `uid too long, max 40
    characters` / `uid contains illegal characters` with a 404 at
    `/api/dashboards/uid/<uid>` — the SAME `failed to save dashboard` line that
    function's own docstring quotes for its half of the layer. The predicate is
    `_grafana_short_uid_defect` and the class is measured, not inherited: see the
    constant block above it and `logs/calibration-step05d-rework-r9-uid-charset.py`
    (31/31 on the pinned image, 121 delivered files in one provisioning run).

    AND THE `title` HALF WAS THE SAME DEFECT, one sentence later. r9 justified the
    repair site with "the title half was already this class" — true of `""` and of
    nothing else. `not doc.get("title")` is PYTHON truthiness, exactly what
    `not doc.get("uid")` had been, so a title of `42`, of `true`, of one U+00A0, or
    of 5001 bytes was 404 at the provisioner and GREEN here (r9 review F1,
    `logs/critic-step05d-r9-title-provisionability.py`). `_grafana_title_defect`
    answers it, and its three bounds are measured because all three CONTRADICT the
    rule the review's own sentence produces: a non-string title is `""` and not a
    type error; the trim's class CROSSES `str.strip()` in both directions; and the
    5000 is counted in UTF-8 BYTES. See the constant block above it.

    A THIRD FIELD OF THE SAME CARRIER IS IN THE SAME CLASS AND WAS FOUND BY ASKING
    RATHER THAN BY REVIEW. A delivered dashboard carries ten top-level keys; the
    other eight were each given the most refusable value their type admits, and one
    is refused — a `tags` member over 50 UTF-8 bytes takes the WHOLE file down with
    the same 404 (`_grafana_tags_defect`). The nine that save are recorded in
    `GRAFANA_DASHBOARD_KEYS_PRICED`, and a delivered key outside that set is printed
    on the gate's own output, because a key nobody has asked is the next round's
    finding and the three rounds before this one each found exactly that.

    A `.json.j2` src is read HERE TOO, with no suffix exemption. The sibling
    inventory check already globs `templates/*dashboard*.json.j2`, so a dashboard
    delivered by `template:` is a dashboard this has to parse, and a suffix skip
    would make "delivered as a template" the one spelling that escapes. The price
    is measured rather than guessed (`logs/rework-step04b-r2-delivery-spellings.log`,
    rows P1/P2 in BOTH modes): Jinja INSIDE a JSON string value — `"title":
    "Third — {{ domain }}"` — is still valid JSON, so a genuinely templated
    dashboard stays GREEN and keeps a readable uid; only Jinja in a STRUCTURAL
    slot is refused, and `test_delivered_dashboards_reference_the_provisioned_uid`,
    which never had a skip, already refused that same file before this one
    stopped skipping. Nothing the guard used to accept is forbidden now.
    """
    body = _read(TASKS)
    if body is None:
        print("FAIL: delivered dashboards parse (tasks/main.yml unreadable)")
        return False
    inventory = _delivered_dashboards(body)
    if not inventory:
        print("FAIL: delivered dashboards parse (no dashboard is delivered)")
        return False
    bad = []
    for name, src, _dest, rendered in inventory:
        if src is None:
            bad.append(f"{name!r}: delivered with no `src:` — nothing on disk to parse")
            continue
        raw = _read(src)
        if raw is None:
            bad.append(f"{src.name}: "
                       f"{_unreadable(src, provisioned=True, rendered=rendered)}")
            continue
        # THE NUMBER RULE IS **DEFERRED** HERE FOR THE REASON `_unreadable` DEFERS IT: an
        # exception is the 1st answer of anything and the engine reaches this rule 5th of
        # six, so a bare `_grafana_provisionable_json(raw)` answers with the number for
        # every document that also breaks an earlier rule. What the `except` still catches
        # — a syntax error, a bare token — the engine really does reach first.
        deferred = []
        try:
            doc = _grafana_provisionable_json(raw, deferred=deferred)
        except (json.JSONDecodeError, GrafanaUnprovisionableJSON) as exc:
            bad.append(f"{src.name}: {exc}")
            continue
        # THE PRESENCE GATE THAT STOOD HERE WAS A **POLICY** CLAIM ASKED BEFORE EVERY ENGINE
        # RULE — the same defect as the chain below, one clause further up, and the reason
        # this clause is now the SHAPE alone. `not doc.get("uid")` is this guard's own
        # requirement and NOT an engine rule: Grafana does not refuse an empty or absent
        # `uid`, it GENERATES a uuid and SAVES the dashboard, which the two non-refusing
        # branches of `_grafana_short_uid_defect` say verbatim. Asked FIRST, it answered for
        # documents the engine stopped on somewhere else entirely. Measured on the pinned
        # `grafana/grafana:13.1.0`, one delivered file per carrier in ONE provisioning run,
        # container log kept, `/api/search` read back (`logs/red-ba6c.py` PART A/B,
        # `logs/red-fb36.py` PART D before it): `uid: ""` and NO `uid` key, each with a
        # 5001-character title, are BOTH `Dashboard title cannot contain more than 5000
        # characters` — the TITLE; `uid: ""` with a 51-byte tag is the TAG; no `uid` with
        # `1e400` is the NUMBER; and each of the two ALONE is IN THE STORE, which is what
        # makes them non-refusals rather than refusals a run failed to trigger.
        #
        # NEITHER HALF IS DROPPED — BOTH MOVE INTO THE ENGINE'S ORDER, which is why this is
        # an ordering and not a deletion. The chain below answers the WHOLE of both classes:
        # a falsy `title` is `_grafana_title_defect`'s (`""` is empty after the trim, and
        # every non-string falsy spelling is what `MustString()` yields `""` for), and a
        # falsy `uid` is the LAST clause's — the non-refusing half `fb36` put after the tag.
        # So this row stays RED for every carrier the gate used to catch and the SENTENCE is
        # the only thing that moves: all fourteen falsy spellings of the two fields are
        # scored on both texts in `logs/red-ba6c.py` PART F.
        #
        # WHAT STAYS IS THE SHAPE, AND IT IS AN ENGINE RULE AT THE ENGINE'S OWN POSITION.
        # The three predicates take FIELDS and a document that is not an object has none to
        # give — the reason, and very nearly the words, `_unreadable` already carries for
        # this class, the FIRST spelling of this same chain. The engine refuses such a file
        # at the LOAD layer, which is BEFORE every save-time rule below, so asking it here
        # is where the engine asks it; its line is `Dashboard title cannot be empty` — the
        # load-layer rule reading a document with no title — and the sentence quotes it, so
        # the operator greps for what the container really printed. Three spellings of the
        # class, each its own delivered file in the run above (`red-ba6c` A-toparray,
        # A-toparray_num, A-topnumber; `red-579d-r5`/`r6` A-toparray before them): a
        # top-level ARRAY, an ARRAY carrying `1e400`, and a bare `42` are the TITLE at the
        # engine for all three — including the one that also breaks the number rule, which
        # is what puts this clause ahead of the deferred number and not merely beside it.
        if not isinstance(doc, dict):
            bad.append(f"{src.name}: the top level is {type(doc).__name__} and not an "
                       "object, so there are no dashboard fields to read — the provisioner "
                       "refuses the file at the LOAD: `Dashboard title cannot be empty`, "
                       "the load-layer rule reading a document that has no title "
                       "(red-579d-r5 A-toparray, red-ba6c A-toparray)")
            continue
        # THE SAVE LAYER, IN THE ORDER THE ENGINE VALIDATES IT — the same order and the
        # same reason as `_unreadable`'s chain, which is the FIRST spelling of it. A
        # document breaks more than one rule at a time and the operator is told to repair
        # the rule the engine STOPPED on, so an `or` chain that opens with the uid names a
        # field the engine never read. Measured (`logs/red-fb36.py` PART A/C, one delivered
        # file per pair in ONE provisioning run on the pinned `grafana/grafana:13.1.0`,
        # container log kept, every `error=` printed, the round-8 review's PART D carriers
        # among them): a blank-after-trim title with an illegal uid, with a uid TOO LONG,
        # with `1e400` and with a 51-byte tag is the TITLE in all four; an illegal uid and
        # a uid too long each with `1e400` are the UID; `1e400` with a 51-byte tag is the
        # NUMBER. Anti-vacuity in that same run: the legal control is served and each of
        # the six rules ALONE is reached and named (PART B). EVERY ADJACENT PAIR OF THIS
        # CHAIN IS ITS OWN DELIVERED FILE — two rounds of 579d were rejected for ordering
        # rules against one shared pivot, which orders each rule against the pivot and
        # nothing among the rest (the table above `GRAFANA_LOG_SAVE`, mem-1785592369-90dd).
        # AND THE uid LINK IS **TWO HALVES**, ONLY ONE OF WHICH IS A REFUSAL — which is why
        # the whole predicate cannot sit in the engine's 4th slot. `_grafana_short_uid_defect`
        # is four rules under one name and TWO of them are not refusals at all: a NON-STRING
        # uid and a uid that is only the engine's trim class are SAVED under a generated uuid,
        # which the predicate's own returned sentence says verbatim ("the provisioner does not
        # refuse it, it GENERATES a uuid"). Asked 4th, a document carrying one of those plus a
        # rule the engine really applies short-circuits on the member that does NOTHING, and
        # the row prints "the provisioner does not refuse it" as THE reason the file was
        # refused. Measured on the pinned image, one delivered file per carrier in ONE run,
        # /api/search read back (`logs/builder-fb36-r2-red.py` PART A/C, the round-9 review's
        # `logs/critic-fb36-uid-nonrefusal-before-number.py` before it): a non-string uid and a
        # trim-class uid, each with `1e400`, are the NUMBER at the engine; each with a 51-byte
        # tag is the TAG; and each ALONE is IN THE STORE afterwards, which is what makes them
        # non-refusals rather than refusals a run failed to trigger.
        #
        # SO THE REFUSING HALF IS ASKED 4TH AND THE OTHER TWO LAST, AFTER THE TAG — an
        # ordering, NOT a deletion. The engine saving a dashboard at an address nothing in
        # this repo can name is a real defect and this row stays RED for it (PART U); it is
        # simply not a refusal, so it cannot outrank a rule the engine did stop on.
        # `_grafana_stored_uid(uid) is not None` is exactly the line between the two halves:
        # it is None for both non-refusals and a string for both refusals, so no member is
        # asked twice and none is dropped. `_unreadable`'s chain — the FIRST spelling of this
        # order — now carries the SAME split (task-1785624345-a15c): `refuses_uid` in the 4th
        # slot, the whole predicate LAST, and a `log=None` clause of its own for the members
        # the engine prints no line for. It was REPAIRED and not merely filed, on the separate
        # delivered-file set it needed — every carrier a raw `0xff` inside a JSON string
        # (`logs/builder-a15c-red.py` PART A/C/D/E, one delivered file per ADJACENT PAIR in
        # ONE run on the pinned image; PART F prints the two spellings agreeing on every
        # carrier in THAT set — all 13 rule carriers — while the readable set still needs
        # its own carriers and its own run, BANKED AS `task-1785635701-d2fd` rather than
        # left as prose. The two sets are DISJOINT AND NOT A PARTITION: this row reaches
        # `_unreadable` only on the `raw is None` branch, which `continue`s, so no delivered
        # file is in BOTH; and the two further `continue` exits between that branch and this
        # chain — the parse `except` and `not isinstance(doc, dict)` — leave a file that
        # DECODES but never becomes an object in NEITHER, measured by
        # `logs/builder-a15c-r4-red.py` PART D at THIS text — D5 delivers three top-level
        # ARRAYs and prints 0 reaching `_unreadable`, 0 entering the chain, row RED naming
        # every one. `logs/critic-a15c-r3-neither-set.py` measured the same class against the
        # EARLIER `821b687f6267` text, whose "exactly ONE" sentence this clause replaces, so
        # it is RED here for that retirement alone — a citation is only worth its VERDICT at
        # the sha it SHIPS at, and that one is green at no text carrying this sentence,
        # mem-1785636803-90cb).
        number = deferred[0] if deferred else None
        uid = doc.get("uid")
        refuses_uid = isinstance(uid, str) and _grafana_stored_uid(uid) is not None
        defect = (_grafana_title_defect(doc.get("title"))
                  or (_grafana_short_uid_defect(uid) if refuses_uid else None)
                  or (None if number is None else f"{number}")
                  or _grafana_tags_defect(doc.get("tags"))
                  or _grafana_short_uid_defect(uid))
        if defect:
            bad.append(f"{src.name}: {defect}")
            continue
        # PRINTED, NEVER FAILED, AND ON ITS OWN LINE. Grafana adds dashboard fields
        # between releases, so reddening for an inert new one is the false refusal this
        # file pays to avoid everywhere else — but three consecutive reviews of this task
        # found the defect in a key of the same carrier that no round had looked at, and a
        # bound nothing prints is a bound the next reader is never told. It is a separate
        # `print` rather than a clause of the row's own summary because
        # `logs/red-step05d-rework-r9-critic-recheck.py` rebuilds this file by replacing
        # that summary's exact source text, and another hat's evidence keeps running
        # unedited. On the tree as delivered this line does not appear at all.
        unpriced = sorted(set(doc) - GRAFANA_DASHBOARD_KEYS_PRICED)
        if unpriced:
            print(f"note: {src.name} carries top-level key(s) {unpriced} whose save-layer "
                  "behaviour is unmeasured — see GRAFANA_DASHBOARD_KEYS_PRICED")
    ok = not bad
    # THE SENTENCE GREW AT ITS END ON PURPOSE. Four earlier harnesses attribute a
    # failure to this row by the substring `parse and carry uid+title`
    # (`logs/review-step04b-r5-pve-case.py`, `logs/rework-step04b-r4-inventory-content.py`,
    # `-r5-subdir-and-keys.py`, `-r6-pve-token-case.py`), so the new claim is appended
    # rather than spliced in — another hat's evidence keeps running unedited.
    print(f"{'OK' if ok else 'FAIL'}: all {len(inventory)} delivered dashboard(s) parse and carry "
          f"uid+title the provisioner will save (problems={bad})")
    return ok


def test_delivered_dashboards_have_distinct_uids() -> bool:
    """No two delivered dashboards may claim one uid, or one dest path.

    STEP 4B IS WHERE THIS STOPS BEING HYPOTHETICAL: until today the role
    delivered ONE dashboard, so a collision needed two files that did not exist.
    4b adds the second and 4c a third, and the provider they share
    (`grafana-dashboards.yml.j2`) has `foldersFromFilesStructure: false`, so
    every JSON lands in one flat namespace keyed by the dashboard's own `uid`.

    MEASURED, not read off the docs, on grafana/grafana:13.1.0 at the delivered
    modes (`logs/calibration-step04b-uid-collision.py` / `.log`):

        U0  two dashboards, DISTINCT uids            both land — /api/search: 2  (control)
        U1  two dashboards, the SAME uid             /api/search: 1
        U2  U1 with the two FILE NAMES swapped       /api/search: 1, the OTHER one wins

    and on the losing rows the server logs, every poll:

        level=warn msg="the same UID is used more than once" uid=… times=2 providers=[homelab]
        level=warn msg="dashboards provisioning provider has no database write
                        permissions because of duplicates" provider=homelab

    Two things make it worth a check of its own rather than a note. First the
    blast radius is the WHOLE PROVIDER, not the colliding pair — the provider is
    told it has no write permissions, so the existing homelab dashboard stops
    being updated too. Second U2: which of the two survives flipped when only the
    FILE NAMES changed, so the author cannot predict which dashboard they lost.
    The server stays HEALTHY throughout — no crash, no error level, just a
    dashboard that is quietly not there, which is why 4d's operator would have
    had to catch it by noticing an absence.

    AND "THE SAME uid" IS THE uid THE ENGINE SAVES UNDER, NOT THE ONE ON DISK.
    The provisioner trims a class off both ends before it stores anything
    (`GRAFANA_SHORT_UID_TRIM`), so two dashboards whose uids differ only by a
    trailing member of it are ONE address in the store — and this collision is
    the one NOTHING warns about. Measured in its own provisioning run, two such
    pairs plus a legal control (`logs/red-579d-r9-collision-detail.py` / `.log`,
    9/9): one file of each pair is simply absent from `/api/search`, the survivor
    is the LAST by file name in both pairs, and the whole container log carries
    ZERO `the same UID is used more than once` lines, ZERO `no database write
    permissions` lines and no `error=` for any of the four. Grafana's own dedupe
    reads the uid AS DELIVERED — the very string this row used to compare — so
    both layers called the pair distinct while the store held one dashboard. The
    control IS served in that same run, so the provider kept its writes and a
    missing dashboard is the collision and not a lockout.

    SO THERE ARE TWO COLLISIONS AND THE BRANCH BETWEEN THEM ASKS THE ENGINE'S
    OWN QUESTION: is ANY delivered spelling duplicated (`len(spellings) <
    len(claims)`), which is what Grafana's dedupe answers to — NOT whether all
    of them are equal, which is a different question and wrong on every mixed
    case. Carried both ways in ONE container (`logs/red-579d-r10.py` PART A):
    provider `pb` delivers FOUR files under THREE spellings with one of them
    repeated and the engine emits `the same UID is used more than once`
    (times=2) AND the `provider=pb` write lockout; provider `pc` delivers two
    files under two spellings with none repeated and the same engine says
    nothing about it while still serving only ONE of the two. A mixed set is
    therefore BOTH — the loud sentence for the repeated spelling, plus the trim
    clause for the files no warning can name — and it is printed as both.

    AND THE TWO LAYERS TAKE TWO DIFFERENT KEYS, WHICH IS WHY THERE ARE TWO
    LOOPS. The uid the engine STORES is what one dashboard can lose to another,
    so the grouping above is on that. Its DEDUPE — the thing that warns and
    disables the writes — reads the uid AS DELIVERED, and those two part company
    on a uid the engine addresses itself: a non-string uid and one that is only
    the trim class each get a freshly generated uuid (calibration C2,
    `red-579d-r9-uid-trim-class` `allem`), so nothing can be LOST to them and
    they are rightly skipped by the stored grouping — but the same delivered
    spelling twice is still a duplicate to the dedupe. It stood here that they
    "can collide with nothing"; that is true of the address and FALSE of the
    warning, and it left the loudest event this row exists for invisible.

    MEASURED, one container, one delivered file per case, the stored uid read
    back over the HTTP API (`logs/red-579d-r11.py` PART A; the review's
    `logs/critic-579d-r10-dedupe-key.py` B1 found it):

        ra  TWO files, ONE empty-trimming spelling (U+00A0)   LOUD: `the same
            UID is used more than once` times=2, and the provider's writes are
            disabled — while BOTH dashboards are served, under uuids
        rc  TWO files, TWO DISTINCT empty-trimming spellings   SILENT, both
            served, nothing lost
        rb  TWO files, the NON-STRING uid `42` twice           SILENT, both
            served
        ta  TWO files, the uid `""` twice                      SILENT, both
            served — the dedupe SKIPS the empty key

    `ra` against `rc` is what makes the key the DELIVERED SPELLING and not "does
    it trim empty": both of `rc`'s trim to the same empty string and the engine
    says nothing about them. `rb` is why the multiset is fenced to a `str` uid.
    So a repeated spelling in that class is reported below on the DELIVERED
    string, with no claim that a dashboard was lost, and every other repeated
    spelling is already reported by the stored grouping — equal spellings trim
    to equal stored uids, so those files are one bucket there.

    AND THE KEY IS A NON-EMPTY DELIVERED SPELLING, WHICH IS WHY THE LOOP BELOW
    ASKS FOR ONE. "The engine invents this dashboard's address" is a class with
    TWO members for a `str` uid — a non-empty run of the trim class, and `""` —
    and the dedupe answers them oppositely: `ta` above is silent and serves
    both, where `ra` is loud. That is the WHOLE class and not a sample: all 25
    codepoints of `GRAFANA_SHORT_UID_TRIM` plus a two-character member, each
    delivered twice under its own provider, 28 providers in ONE container —
    26 of 26 loud with the warning AND the lockout, `ta` alone silent
    (`logs/red-579d-r12.py` PART A; the review's
    `logs/critic-579d-r11-empty-uid.py` `sa` is the same answer in another
    engine, and `sd`/`sc` and `tg`/`tf` are anti-vacuity in both runs). `""` is
    not exotic — it is what a hand-written dashboard and several Grafana export
    paths carry — so without the fence this row printed a provider-wide write
    lockout over a delivery the engine serves in full, the wrong-verdict-on-a-
    served-dashboard class `GRAFANA_SHORT_UID_TRIM` says it pays to avoid.
    Nothing is hidden by the fence: an empty uid is still an address no line in
    this repo can name, and `test_delivered_dashboards_parse_as_dashboards`
    names it on the row whose subject IS the address (PART B: that row still
    FAILs, and names both files, over the tree this one passes).

    The dest half is the same collision one layer down and needs no server to
    see: two delivery tasks writing one path leave one file, so one dashboard is
    never delivered at all.

    A file this cannot read or parse is REPORTED here, not skipped — a uid it
    cannot read is a uid it cannot prove distinct — even though
    `test_delivered_dashboards_parse_as_dashboards` prints the better reason.
    THAT INCLUDES A `.j2` SRC, and it is stated because the first spelling of
    this check exempted one: `if src.suffix == ".j2": continue`, copied from a
    sibling, which made the docstring above false and left the collision this
    check exists to catch invisible in TWO delivery spellings — `template:` out
    of `templates/` AND `copy:` of a `files/…json.j2`, both measured GREEN at
    PASS 13/13 with the uid duplicated, both RED once the skip is gone
    (`logs/rework-step04b-r2-delivery-spellings.log`, rows R1/R2 in both modes).
    A check that reads a uid off SOME of the delivered dashboards cannot prove
    any of them distinct.
    """
    body = _read(TASKS)
    if body is None:
        print("FAIL: delivered dashboards have distinct uids (tasks/main.yml unreadable)")
        return False
    inventory = _delivered_dashboards(body)
    if not inventory:
        print("FAIL: delivered dashboards have distinct uids (no dashboard is delivered)")
        return False
    bad, uids, dests, delivered = [], {}, {}, {}
    for name, src, dest, rendered in inventory:
        dests.setdefault(dest, []).append(name)
        if src is None:
            bad.append(f"{name!r}: delivered with no `src:` — no uid on disk to compare")
            continue
        raw = _read(src)
        if raw is None:
            bad.append(f"{name!r}: src {src} "
                       f"{_unreadable(src, provisioned=True, rendered=rendered)}")
            continue
        try:
            uid = _grafana_provisionable_json(raw).get("uid")
        except (json.JSONDecodeError, GrafanaUnprovisionableJSON, AttributeError) as exc:
            bad.append(f"{src.name}: unparseable, so its uid is unknown ({exc})")
            continue
        if isinstance(uid, str):
            # THE DEDUPE'S OWN KEY, taken before the skip below. Grafana warns and disables
            # the writes on the uid AS DELIVERED, which is a different string from the one
            # it stores under and exists for dashboards it stores under no uid of theirs
            # at all.
            delivered.setdefault(uid, []).append(src.name)
        stored = _grafana_stored_uid(uid)
        if stored is None:
            # The engine picks this dashboard's address itself — a non-string uid, or one
            # that is only the trim class, gets a freshly generated uuid — so nothing can
            # be LOST to it and there is no address here to compare. Its delivered spelling
            # is still counted above, because the dedupe reads that one. It is not passed
            # over in silence either: `test_delivered_dashboards_parse_as_dashboards` names
            # it, on the row whose subject is the address.
            continue
        uids.setdefault(stored, []).append((src.name, uid))
    for spelling, files in sorted(delivered.items()):
        if len(files) > 1 and spelling and _grafana_stored_uid(spelling) is None:
            # THE COLLISION WITH NO ADDRESS. Every OTHER repeated spelling is already in one
            # bucket below — equal strings trim to equal stored uids — so this reports the
            # class that grouping cannot hold: files the engine saves under uuids of its
            # own, which are duplicates to its dedupe all the same. Nothing here is lost,
            # which is why it does not borrow the U1/U2 sentence.
            #
            # AND `spelling` IS ASKED FOR ITSELF, because `_grafana_stored_uid(s) is None`
            # names TWO members for a `str` — a NON-EMPTY string of the trim class, and the
            # EMPTY STRING — and the engine's dedupe keys on the delivered uid only when it
            # is non-empty. `""` twice is SILENT and both are served (`red-579d-r12` PART A
            # `ta`, `critic-579d-r11-empty-uid` `sa`), so without this clause the row claims
            # a provider-wide write lockout over a delivery the engine serves in full. The
            # fence is the engine's own and not a proxy for it: every NON-empty member stays
            # here, all 26 of them measured loud in one container (PART A `m00`..`m24`,
            # `mm`).
            bad.append(f"dashboard uid {spelling!r} is delivered by {sorted(files)} — the engine "
                       "SAVES each of them (the uid is only its trim class, so each gets a "
                       "generated uuid and none is lost), but its dedupe reads the uid AS "
                       "DELIVERED, so one spelling twice is still `the same UID is used more "
                       "than once` and the WHOLE provider's writes are disabled: every "
                       "dashboard it owns stops being updated (red-579d-r11 PART A `ra`, "
                       "critic-579d-r10-dedupe-key B1). Two DISTINCT members of the trim class "
                       "are silent and lose nothing (`rc`), so it is the repeated spelling and "
                       "not the empty address that does this")
    for uid, claims in sorted(uids.items(), key=lambda kv: str(kv[0])):
        if len(claims) > 1:
            files = [name for name, _delivered in claims]
            spellings = sorted({delivered for _name, delivered in claims})
            if len(spellings) < len(claims):
                # IS ANY DELIVERED SPELLING DUPLICATED — the engine's own question, asked
                # the engine's way. Its dedupe reads the uid AS DELIVERED, so ONE repeated
                # spelling is enough to warn and to disable the provider's writes, whatever
                # the other claims on the same stored address look like. A set-shaped test
                # ("are ALL the spellings equal") answers a different question and gets the
                # mixed case backwards: `red-579d-r10` PART A delivers FOUR files under
                # THREE spellings with one of them repeated and the engine emits both
                # `the same UID is used more than once` (times=2) and the `provider=pb`
                # lockout, while `pc` — two files, two spellings, nothing repeated — is
                # silent in that same container.
                #
                # AND THE MIXED CASE IS BOTH THINGS AT ONCE, so it gets both clauses: the
                # duplicated pair is what the warning names, and the trimmed-equal files
                # collide beside it with nothing naming them at all.
                #
                # AND THE SENTENCE HAS TO NAME A STRING THAT EXISTS. This row's key is the
                # STORED uid; the engine's warning carries the uid AS DELIVERED (2 lines to 0,
                # `critic-579d-r10-dedupe-key` A2). So the question is whether a trim moved
                # anything — `spellings != [uid]` — and NOT whether there is more than one
                # spelling, which is silent on the case where ONE spelling that the engine
                # trims is delivered twice: that printed a uid in neither file and in no log
                # line, and said nothing about a trim.
                trimmed = ("" if spellings == [uid] else
                           f" — and they are delivered as {spellings!r}, which the engine "
                           f"TRIMS to that one uid, so the warning names those and not the "
                           f"{uid!r} this row keys on"
                           + ("" if len(spellings) == 1 else
                              ", and the file(s) whose spelling is delivered once collide "
                              "here with nothing naming them at all")
                           + " (red-579d-r10 PART A `pb`, red-579d-r11 PART E)")
                bad.append(f"dashboard uid {uid!r} is claimed by {sorted(files)} — grafana keeps ONE "
                           "of them and disables the provider's writes (calibration rows U1/U2)"
                           + trimmed)
            else:
                # SAME COLLISION, NO WARNING AT ALL — so it needs its own sentence. The
                # engine dedupes on the uid AS DELIVERED and stores under the TRIMMED one,
                # so these files agree they are distinct at the layer that reports and
                # collide at the layer that serves. No spelling here is delivered twice,
                # which is exactly why nothing is logged.
                bad.append(f"dashboard uid {uid!r} is claimed by {sorted(files)} as {spellings!r} "
                           "— the engine TRIMS those to one uid and keeps ONE file, silently: no "
                           "duplicate-uid warning, no write lockout, no `error=` for any of them "
                           "(red-579d-r9-collision-detail B1/B2/C3, red-579d-r10 PART A `pc`)")
    for dest, tasks in sorted(dests.items()):
        if len(tasks) > 1:
            bad.append(f"{dest} is written by {sorted(tasks)} — one file, one dashboard lost")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: {len(inventory)} delivered dashboard(s) hold "
          f"{len(uids)} distinct uid(s) at {len(dests)} distinct dest(s) (problems={bad})")
    return ok


def test_delivered_dashboards_have_distinct_titles() -> bool:
    """No two delivered dashboards may land in ONE FOLDER under one title.

    THE SECOND CAUSE OF THE LOCKOUT THE ROW ABOVE OWNS THE SENTENCE FOR. Two
    delivered dashboards with the SAME `title` and distinct, legal, non-trimming
    uids take the very same provider-wide write disable — "every dashboard it
    owns stops being updated" — by a route that row cannot see, because its key
    is the uid and this collision is not one. Found by the review of
    `task-1785571102-579d` while probing the fence that round 12 built, filed
    rather than folded into it, and measured there twice in two containers
    (`logs/critic-579d-r12-duplicate-title-lockout.py` 7/7,
    `-empty-uid-same-title.py` 6/6, provider `eg`).

    AND THE ENGINE NAMES THE TITLE — NOT THE FILES. Rounds 1..4 of this row closed
    their verdict with "the engine gives no message of its own … no title line",
    and five containers across two tasks agreed, because all five share ONE
    apparatus decision: they keep only log lines matching `more than once` or the
    lockout string, and Grafana's title line carries NEITHER. Printed with no
    keyword filter at all the whole log is two lines, and the cause sits
    immediately above the effect (`logs/critic-9ffc-r4-unfiltered-log.py` /
    `.log`, 5/5, and `logs/red-9ffc-r5-title-line.py` / `.log` W1/W2 in a second
    container):

        level=warn msg="dashboard title is not unique in folder" orgId=1
                       title="…" folderID=0 times=2 providers=[ud]
        level=warn msg="dashboards provisioning provider has no database write
                        permissions because of duplicates" provider=ud orgId=1

    So the verdict below QUOTES that message, the way this file quotes every other
    engine rule. What the engine still does not give is the half this row exists
    for: it names a TITLE and a folder id, and the operator holds FILES.

    AND `times` FOLLOWS THE GROUP, so the sentence takes its pronouns from the
    group's size instead of hardcoding a pair: three files under one title are
    `times=3` and all three are served (`red-9ffc-r5-title-line` W6,
    `logs/critic-9ffc-r4-title-and-uid.py` Z6) — and the repo delivers exactly
    three dashboards, so a hardcoded "both" would mis-count in the shipping tree.

    THE SERVING CLAIM IS CONDITIONED, BECAUSE THE CHEAPEST REAL ROUTE HERE IS A
    COPY AND A COPY CARRIES THE uid TOO. Two files under one title and ONE uid
    spelling: the engine prints BOTH of its lines and keeps ONE of the two (W7,
    Z3/Z4), while the uid row one screen above prints `grafana keeps ONE of them`
    over that same tree on the same gate output.

    AND IT IS CONDITIONED ON **BOTH** OF THAT ROW'S KEYS, BECAUSE A FILE IS LOST
    BY TWO ROUTES AND ONLY ONE OF THEM IS LOUD. The engine DEDUPES on the uid as
    delivered and STORES under the trimmed one, and those part company: two
    delivered spellings differing only by a member of `GRAFANA_SHORT_UID_TRIM` are
    distinct to the dedupe and ONE address to the store. Measured, four providers
    in one container on the pinned image
    (`logs/critic-9ffc-r5-trim-uid-under-one-title.py` / `.log`, 8/8):

        wa  one title; uids `X` and `X`+U+00A0   SERVED 1/2 — title line, LOCKOUT,
                                                 and NO uid line at all
        wb  DISTINCT titles, same uid shape      served 1/2, silent — so the lost
                                                 file is the trim's, not the title's
        wc/wd  the accept side and the COPY      2/2 served / 1 served, both loud

    Round 5 conditioned on `claimed` alone, so over `wa` the clause was KEPT and
    the guard printed `grafana serves all 2 of them` on the very gate output where
    the row above printed `keeps ONE file, silently` — the self-contradiction
    `red-9ffc.py` R10d asserts is gone, standing on the key R10d does not carry.
    R10e/R10f are its second member. The two causes take two SENTENCES because
    their engine evidence is opposite: the repeated spelling has `the same UID is
    used more than once` to go read, and the trim collision has nothing, which is
    what makes this sentence load-bearing rather than merely redundant (C4).

    AND "THE TRIM COLLISION HAS NOTHING" IS A CLAIM ABOUT A LOG, WHICH IS THE
    CONTAINER'S AND NOT THIS GROUP'S. The premise is that the group's two
    spellings differ so the dedupe cannot fire FOR THE PAIR — true — and the
    conclusion was that the engine prints no uid line of any kind. A third
    delivered file repeating one of those spellings makes it fire on that
    spelling, and the operator was told there was nothing to grep. Measured, two
    containers on the pinned image, two providers in ONE container with every
    title unique and no spelling crossing a provider
    (`logs/critic-9ffc-r8-crossgroup-repeat.py` / `.log`, 13/13, re-run unedited
    at round 9's hands in `logs/builder-9ffc-r9-engine-recheck.log`):

        ga  group `S` and `S`+U+00A0 (ONE address); an        `the same UID is used
            OUTSIDER under another title carries `S`           more than once`
                                                              uid=`S` times=2,
                                                              served 1/3, LOCKOUT
        gb  THE ANTI-VACUITY CONTROL, same container:         NO uid line — and
            that tree with the outsider elsewhere             there the sentence is
                                                              TRUE

    So the sentence was right at `gb` and wrong at `ga` in one run, and the
    difference is the OUTSIDER. `loud_trim` asks the engine's own dedupe predicate
    at the engine's own scope — `claimed` was kept GLOBAL for exactly this reason
    — and the silence is claimed only where that list is empty. `red-9ffc.py`
    R13a/R13b hold both members and R13c holds the calibration.

    Where every spelling is distinct AND no two trim together the claim is kept
    and measured (W1, `wc`, scope run `ta`): both served, nothing looks wrong on
    the day it ships, and the damage is entirely in the future, in every later
    edit silently not being applied.

    AND THE SILENT SCOPES ARE SILENT IN BOTH OUTPUTS. The same title in two
    folders — `foldersFromFilesStructure` subdirectories, or two providers with
    distinct `folder:` — prints NO title line either (W4/W5), which is what lets
    this row stay GREEN over them without leaving an engine line unexplained. The
    scope run below measured those trees for the LOCKOUT only; the title line was
    handed over unmeasured by the round-4 review and is carried here.

    THIS IS A ROW OF ITS OWN AND NOT A CLAUSE OF THE uid ROW (DEC-183). Both
    collisions end in one lockout, so folding them was the live alternative. They
    are separated because they take DIFFERENT KEYS, and a row that carries two
    keys cannot keep its own name true: the uid row groups on the uid the engine
    STORES (`_grafana_stored_uid`, two loops and a fence measured over 28
    providers), this one groups on the title AS DELIVERED inside a FOLDER. The
    two are independently reachable — a tree can be RED here and GREEN there and
    the reverse — and `logs/red-9ffc.py` R1e carries exactly that: over the
    colliding tree this row FAILS while the uid row prints `problems=[]`.

    THE SCOPE IS THE FOLDER, AND IT IS MEASURED HERE RATHER THAN INHERITED FROM
    THE uid TRACKER'S. That one is GLOBAL over delivered spellings
    (`red-579d-r11-crossprovider` X1) and the review's measurement of this one
    was taken inside ONE provider in ONE folder, so it could not say which axis
    carried it; a claim about a scope needs a carrier at that scope. Eight
    providers in one container on the pinned `grafana/grafana:13.1.0`, every uid
    distinct and legal so the title is the only variable
    (`logs/red-9ffc-title-scope.py` / `.log`, 8/8):

        ta  one provider, one folder, SAME title        LOCKOUT   (the finding)
        tb  one provider, one folder, distinct titles   silent    (says NO)
        tc/td  TWO PROVIDERS, one file each, SAME       BOTH providers locked
               title, both in the General folder        out — NOT provider-scoped
        te  one provider, foldersFromFilesStructure,    silent, both served in
            SAME title in two subdirectories            two folders
        tf/tg  two providers, distinct `folder:`,       silent
               SAME title
        th  one provider, NO folders flag, SAME title   LOCKOUT — the provider
            in two subdirectories                       RECURSES and both land in
                                                        one folder

    So the collision is per-FOLDER and global ACROSS PROVIDERS, and `th` is why
    the folder below is read off the provider's flag and not off the dest
    directory: without `foldersFromFilesStructure` a subdirectory is not a
    folder, which DEC-074 asserted and no run had shown.

    AND THE KEY IS THE TITLE **AS DELIVERED**, WHICH REFUTED THIS ROUND'S OWN
    PREDICTION. I wrote down before the run that the tracker would see the title
    the engine SAVED, so that `_grafana_title_defect`'s trim class would make two
    spellings one key. It does not (`logs/red-9ffc-title-key.py` / `.log`, 8/8):

        ua  "…probe" and "…probe" + U+FEFF   STORED UNDER ONE TITLE, both served,
        ub  "…probe" and "…probe" + U+0020   NO lockout — either way
        uf  ONE title delivered twice        LOCKOUT, in that same container
            verbatim

    `uf` is what makes `ua`/`ub` a key and not a container with duplicate
    detection off. So this row compares the delivered string EXACTLY: a
    `title.strip()` would print a provider-wide lockout over a delivery the
    engine serves in full and says nothing about, the
    wrong-verdict-on-a-served-dashboard class this file pays to avoid everywhere
    else. `red-9ffc.py` R4 holds that accept side.

    AND **THE DELIVERED STRING IS THE ONE GO DECODED**, WHICH IS THE OTHER HALF
    OF THAT SPECIFICATION AND NOT THE SAME HALF. "As delivered" says WHEN the
    engine takes the string — before its own save-time trim — and says nothing
    about WHOSE DECODER produced it, and a delivered file meets Go's before it
    meets anything else. So the key below is `_grafana_saved_text(title)`, as it
    is in BOTH the other readers of a delivered title in this file
    (`_grafana_dashboard_title`, `_grafana_title_defect`). Measured, four
    providers in ONE container on the pinned `grafana/grafana:13.1.0` with the
    stored titles read back over the HTTP API
    (`logs/critic-9ffc-surrogate-title.py` / `.log`, 11/11):

        sa  "…probe" + \\ud800 vs "…probe" + \\udc00   LOCKOUT, both served,
        sb  "…probe" + \\ud800 vs the LITERAL U+FFFD   ONE stored title
        sc  "…probe one" vs "…probe two"             silent — this run says NO
        sd  "…probe" + \\ud800 twice VERBATIM          LOCKOUT: a KEY difference,
                                                     not detection switched off

    Round 2 of this row keyed on `json.loads`'s string and was PASS 22/22 rc=0
    over `sa` and `sb`, printing "3 distinct title(s)" where the engine held two
    (that harness's B1/B2; the verbatim twin B3 was already caught, so the gap
    was the DECODE and not the delivery path). `red-9ffc.py` R7a/R7b/R7c hold
    it now.

    THE TWO NORMALISATIONS MUST NOT BE CONFUSED THOUGH BOTH ARE "TIDY THE
    TITLE", and the difference is checkable rather than preferred: a
    deterministic substitution on the key can only MERGE groups, so it only ever
    ADDS reds and every red it adds is a tree the engine locks out — it cannot
    invent a false refusal. A trim can, and does (K1/K2, R4).

    AND A FILE THE PROVISIONER NEVER SAVES IS OUTSIDE THIS ROW, WHOLE-CLASS.
    `_grafana_title_defect` has four members and each one was delivered TWICE
    under its own provider in the key run: `""` (refused at the LOAD, `uc`), a
    non-string (`MustString()` yields `""`, so the LOAD again, `ug`), a title
    that is only the trim class (refused at the SAVE, `ud`) and one over 5000
    UTF-8 bytes (the SAVE, `uh`). None of the four is served and NONE takes the
    lockout — a dashboard the engine never registers collides with nothing — so
    a second sentence here would be a claim about a dashboard that does not
    exist. They are not passed over in silence either:
    `test_delivered_dashboards_parse_as_dashboards` names every one of them, on
    the row whose subject IS the title the provisioner will save (`red-9ffc.py`
    R5: that row FAILS and this one prints `problems=[]` over the same tree).

    AND THE TITLE IS ONE OF THREE FIELDS THAT CAN GET A FILE REFUSED — the fence
    asked ONE of them for two rounds. A defective TITLE can only ever group with
    a byte-identical title, so the MIXED shape is unreachable for that predicate
    and reachable for the other two, which is why no run met it until one asked.
    Measured on the pinned image, ONE PROVIDER PER CASE and EVERY PROVIDER'S
    TITLE UNIQUE IN THE CONTAINER — the collision is global across providers, so
    a shared title confounds every row (`logs/critic-9ffc-r3-unsavable-isolated.py`
    / `.log`, 7/7, and that harness's own killed sibling is the confound):

        xb  one title; the second uid 41 characters   SILENT, ONE served
        xc  one title; the second uid ` ` and `!`     SILENT, ONE served
        xd  one title; the second a 51-BYTE tag       SILENT, ONE served
        xf  one title; BOTH uids 42 characters        SILENT, NEITHER served
        xa/xe  the savable pair and the distinct      LOCKOUT / silent — the
               pair, in that same container            two directions

    Over each of those the row printed a provider-wide lockout the engine does
    not take, and pointed at log lines the container does not carry.
    `red-9ffc.py` R8a…R8d hold the silence now, and the gate stays RED at the
    parse row, which prints the TRUE cause.

    THE `uid` PREDICATE IS ASKED THROUGH `_grafana_stored_uid`, THOUGH, AND NOT
    WHOLE — and that is the difference between removing a false sentence and
    installing a false GREEN. Only two of `_grafana_short_uid_defect`'s four
    members are refusals. The other two are the ones its own docstring calls
    SAVED: a non-string uid and a uid that is only the trim class are stored
    under a GENERATED UUID, so the dashboard registers, its title reaches the
    store, and the provider IS locked out. Measured, seven providers in one
    container with every uid SPELLING distinct (`logs/red-9ffc-r4-uuid-uid-title.py`
    / `.log`, 8/8):

        yc  one title; the second uid `42`         LOCKOUT, BOTH served
        yd  one title; the second uid U+2003       LOCKOUT, BOTH served
        yf/yg  the same two uids with DISTINCT     silent — so the lockout is
               titles                               the TITLE's, not the uid's
        ye  one title; the second uid 41 chars     SILENT, ONE served — the
                                                    bridge to `xb`

    `_grafana_stored_uid(uid) is not None` is exactly the line between the two
    halves: None for those two members, a string for the charset and length
    refusals. `red-9ffc.py` R9a/R9b hold the RED side. The first run of that
    harness gave two providers ONE empty-trimming uid spelling and the engine
    locked BOTH out on `the same UID is used more than once` — the uid tracker
    is global over spellings too (`red-579d-r11` `ra`/`rc`); the confounded log
    is kept beside the clean one.

    A file this cannot read or parse is REPORTED here, not skipped, for the
    reason the uid row states: a title it cannot read is a title it cannot prove
    distinct.
    """
    body, provider = _read(TASKS), _read(DASHBOARDS_TPL)
    if body is None or provider is None:
        print("FAIL: delivered dashboards have distinct titles (a source file is unreadable)")
        return False
    inventory = _delivered_dashboards(body)
    if not inventory:
        print("FAIL: delivered dashboards have distinct titles (no dashboard is delivered)")
        return False
    bad, titles, claimed, held = [], {}, {}, {}
    # WHICH FOLDER A DELIVERED FILE LANDS IN IS A PROPERTY OF THE PROVIDER, NOT OF THE
    # DEST. With `foldersFromFilesStructure: false` the provider recurses and everything
    # under its path flattens into ONE folder, subdirectory or not (scope run `th`), so the
    # dest cannot separate two titles; with the flag ON the subdirectory IS the folder
    # (`te`). The repo declares one provider and the deliveries all write inside its path
    # (`test_dashboards_are_delivered_where_grafana_looks` keeps those three paths equal),
    # so a second provider would put a delivered file somewhere this reader cannot place
    # and is reported rather than assumed away.
    providers = _provisioning_entries(provider, "providers")
    if len(providers) != 1:
        bad.append(f"{DASHBOARDS_TPL.name} declares {len(providers)} provider(s) — the folder a "
                   "delivered dashboard lands in is read off THE provider, and with none or "
                   "several this row cannot say which one owns a dest (the collision is "
                   "per-FOLDER and global across providers: red-9ffc-title-scope tc/td, te)")
    from_files = (len(providers) == 1
                  and str(providers[0].get("foldersFromFilesStructure", "")).lower() == "true")
    for name, src, dest, rendered in inventory:
        if src is None:
            bad.append(f"{name!r}: delivered with no `src:` — no title on disk to compare")
            continue
        raw = _read(src)
        if raw is None:
            bad.append(f"{name!r}: src {src} "
                       f"{_unreadable(src, provisioned=True, rendered=rendered)}")
            continue
        try:
            doc = _grafana_provisionable_json(raw)
            title, uid, tags = doc.get("title"), doc.get("uid"), doc.get("tags")
        except (json.JSONDecodeError, GrafanaUnprovisionableJSON, AttributeError) as exc:
            bad.append(f"{src.name}: unparseable, so its title is unknown ({exc})")
            continue
        if (_grafana_title_defect(title)
                or _grafana_tags_defect(tags)
                or (_grafana_stored_uid(uid) is not None
                    and _grafana_short_uid_defect(uid))):
            # THE ENGINE NEVER REGISTERS THIS ONE, so it collides with nothing. That law is
            # measured (xa..xg, Y1..Y7) and this file spells its condition in THREE
            # predicates, all three asked in one `or` by the parse row one screen above —
            # a refused `title`, a refused `tags` member, a refused `uid`. The row that
            # owns each defect prints it, and the gate is RED there on every tree below.
            #
            # BUT `_grafana_short_uid_defect` IS NOT A REFUSAL PREDICATE, and taking that
            # `or` whole would put a false GREEN where a false SENTENCE was. Two of its
            # four members are exactly the ones its own docstring calls SAVED: a
            # non-string uid and a uid that is only the engine's trim class are not
            # rejected, the provisioner GENERATES a uuid and stores the dashboard — so its
            # title reaches the store and the provider IS locked out
            # (`red-9ffc-r4-uuid-uid-title` Y4/Y5, both files served; Y6/Y7 are the
            # distinct-title controls that attribute the lockout to the title and not to
            # the odd uid). `_grafana_stored_uid(uid) is not None` is the line between the
            # two halves, because it is None for precisely those two members and a string
            # for the charset and length REFUSALS (xb/xc/Y3, silent, one file served).
            continue
        folder = dest.rsplit("/", 1)[0][len(DASHBOARDS_DIR):].strip("/") if from_files else ""
        # THE KEY IS `_grafana_saved_text(title)` AND NOT `title`, FOR THE REASON EVERY
        # OTHER READER OF A DELIVERED TITLE IN THIS FILE APPLIES IT: the string the engine
        # compares is the one GO decoded, and `\ud800` and `\udc00` are two code points to
        # `json.loads` and ONE U+FFFD to Go. NOT a trim — the trim class is a different
        # layer and the engine is silent there (key run K1/K2, R4). This substitution is
        # ONE-SIDED SAFE where a trim is not: equal strings have equal images, so it can
        # only ADD collisions, and every one it adds is a tree the engine locks out.
        titles.setdefault((folder, _grafana_saved_text(title)), []).append(
            (src.name, title, uid, dest))
        if isinstance(uid, str):
            # THE OTHER ROW'S KEYS, BOTH OF THEM, counted over the WHOLE delivery and not
            # inside a title group: `the same UID is used more than once` is global over
            # delivered SPELLINGS (red-579d-r11 X1) and the STORE is global over trimmed
            # ones. A dashboard on either key is one grafana does not serve, so the serving
            # clause below is conditioned on BOTH — the row above needs both and the clause
            # borrowed one.
            #
            # AND EACH TRACKER KEEPS THE FILES AND NOT A COUNT, because the sentence they
            # gate is about ONE title group and a count cannot say WHOSE file is at risk.
            # Both stay GLOBAL — the engine's are, and rescoping them would be a second
            # wrong answer — so the group below asks them who ELSE claims its address.
            # THE DEST IS THE IDENTITY, NOT `src.name`: this inventory is keyed on the dest
            # because the dest IS the file the engine reads, and two srcs under different
            # roots can carry ONE basename (`builder-9ffc-r8-identity-probe` I2 delivers
            # exactly that tree — with the basename as the identity the outside file counts
            # as this group's and the false claim below comes straight back). The src name
            # rides along in `held` only to be PRINTED, in the same namespace as `names`.
            claimed.setdefault(uid, []).append(dest)
        stored = _grafana_stored_uid(uid)
        if stored is not None:
            # THE ADDRESS THE PROVISIONER SAVES UNDER, the delivering file kept beside it so
            # a claimant outside the group can be named below. `None` is not tracked: the
            # engine generates a uuid there, so no two of them can land on one address and
            # nothing is lost.
            held.setdefault(stored, []).append((dest, src.name))
    for (folder, saved), files in sorted(titles.items()):
        if len(files) > 1:
            # THE FILES THIS SENTENCE IS **ABOUT**, NAMED THE WAY THE ASIDE BESIDE THEM IS.
            # `src.name` is a BASENAME, and the comment fifteen lines above states the fact
            # that makes one unusable as an identity — "two srcs under different roots can
            # carry ONE basename" — draws that conclusion for `claimed`, which keys on the
            # dest, and then printed this group's OWN members by the basename anyway, with
            # `_dest` unpacked in the very comprehension that threw it away. The row exists
            # FOR this mapping: its closing clause is `The mapping from that title back to
            # these N FILES is the one thing it does not give`, and over a colliding tree it
            # gave `['dup-dashboard.json', 'dup-dashboard.json']` — ONE name for two files,
            # on the only failing row of that tree, so that sentence was all the operator
            # got. Measured whole-guard over tempdir trees (`red-9ffc-r13` D1/D3, the pair
            # the review raised in `critic-9ffc-r12-group-member-identity` G1/G3), and it
            # needs no subdirectory at all: `root = TEMPLATES if is_template else FILES`, so
            # two FLAT srcs of one basename under `files/` and `templates/` collapse
            # identically (D2/G2) — the layout this repo actually ships.
            #
            # CONDITIONAL, ON THIS GROUP'S OWN COUNT OF THE BASENAME. The collision is a
            # fact the group already holds, so a member that is unambiguous is printed
            # EXACTLY as it reads today and only the colliding ones are separated (D5 holds
            # both branches in ONE verdict, D4 the untouched pair). That is not taste: this
            # thread's harnesses grep `is delivered by [...]` for a spelling, and every
            # non-colliding verdict in the repo stays byte-identical
            # (`builder-9ffc-r13-collateral`).
            #
            # AND THE DEST IS CUT AT `DASHBOARDS_DIR`, the coordinate `folder` above and
            # `outside` below are both cut at — printed whole it would put the machine's
            # filesystem layout, identical on every line, in front of the operator on every
            # tree this role delivers (D6). The slice is total here for the same reason it
            # is below: a dest that is not under that directory never reaches this loop
            # (:1625-1632 rebuilds the bare-directory dest from the src basename or the
            # entry is skipped), and the one that carries no src dies at the `src is None`
            # branch above.
            basenames = [name for name, _title, _uid, _dest in files]
            names = sorted(name if basenames.count(name) == 1
                           else f"{name} -> {dest[len(DASHBOARDS_DIR):].strip('/')}"
                           for name, _title, _uid, dest in files)
            # GROUPED ON WHAT GO HOLDS, PRINTED AS WHAT IS ON DISK — `_grafana_title_defect`
            # does exactly this one function above. When the delivered spellings differ the
            # operator will grep their own file for a string that is in it, so naming only
            # the decoded title would send them looking for text nothing on disk carries.
            spellings = sorted({title for _name, title, _uid, _dest in files})
            delivered = f"{spellings[0]!r}" if len(spellings) == 1 else f"{spellings}"
            decoded = "" if len(spellings) == 1 else (
                f" — those {len(spellings)} delivered spellings are the ONE title {saved!r} to "
                "GO's decoder (an unpaired surrogate is U+FFFD to it), which is the string the "
                "engine compares")
            # THE SERVING CLAIM IS A SECOND ENGINE CLAIM AND IT IS NOT TRUE OF EVERY MEMBER
            # OF THIS GROUP. A file this delivery loses to the uid is lost by TWO routes and
            # the row above owns both, in two branches: a repeated delivered SPELLING (its
            # dedupe reads the uid as delivered) and two distinct spellings that TRIM to one
            # stored uid (its store keys on the trimmed one). Either costs one file, so the
            # clause is withheld on either and the uid(s) are named instead.
            #
            # AND THE TWO CAUSES GET TWO SENTENCES, BECAUSE THEIR ENGINE EVIDENCE IS
            # OPPOSITE. The repeated spelling has a log line — `the same UID is used more
            # than once` — and the operator can go read it. The trim collision has none OF
            # ITS OWN: the dedupe compares the delivered spellings and THESE TWO differ, so
            # for this pair the engine says nothing about the uid and the guard's sentence is
            # the only thing the operator has (`critic-9ffc-r5-trim-uid-under-one-title`
            # `wa`, served 1/2 with the title
            # line and the lockout but NO uid line, C3/C4; `wb` attributes the lost file to
            # the trim and not to the title, C7) — WHICH IS A CLAIM ABOUT THE PAIR, and the
            # log is the container's, so `loud_trim` below re-asks it at that scope before
            # the sentence is printed. Round 5 conditioned on `claimed` alone and
            # printed `grafana serves all 2 of them` over `wa` on the same gate output where
            # the row above printed `keeps ONE file, silently` (red-9ffc R10e/R10f).
            #
            # AND BOTH LISTS ANSWER ON AN ADDRESS, BECAUSE `claimed` IS THE DEDUPE'S KEY AND
            # ANSWERS "DOES THE ENGINE WARN" — NOT "IS A FILE LOST". A file is lost only
            # when two of them land on ONE stored uid, and where `_grafana_stored_uid` is
            # None there is no such address: the provisioner generates a uuid PER FILE, so a
            # spelling delivered twice is stored twice and BOTH are served. Measured, three
            # providers in one container on the pinned image
            # (`critic-9ffc-r6-empty-trim-repeat`, re-run in `builder-9ffc-r7-engine-recheck`):
            # `za` uid `""` twice and `zb` uid U+00A0 twice are 2/2 SERVED, against `zc`'s 1/2
            # for a normal spelling twice — the calibration where this clause's `does NOT
            # serve` is true. Without the fence the two would be named here on the same gate
            # output where the row above prints `the engine SAVES each of them … and none is
            # lost`, which is the self-contradiction R10d/R10f exist to kill, on a third key.
            # `trimmed` already asked it structurally — `held` only ever keys on a stored uid,
            # so `held.get(None, ())` is empty and the class can never reach that list — and
            # the condition below is the same question asked out loud on the other tracker.
            #
            # THE TWO MEMBERS OF THAT CLASS ALSO PART COMPANY AT THE LOG, which is the second
            # direction this was wrong in and why the fence is not just tidiness: U+00A0 twice
            # IS `the same UID is used more than once` (C5, and the row above prints it, at
            # :5474 fenced on `and spelling`), while `""` twice carries no uid line at all in
            # three polls — so naming it here sent the operator to grep a string the container
            # never printed.
            # AND ALL OF IT IS ASKED **OF THIS GROUP**, ON TRACKERS THAT STAY GLOBAL. A
            # collision costs a file wherever it happens, but WHICH file is at risk depends
            # on who the two claimants are, and until this round the two lists read the
            # global trackers as if every claimant were this group's. Measured, five
            # providers in one container (`critic-9ffc-r7-crossgroup-serving` H4/H5): a group
            # whose file shares a uid with a dashboard under ANOTHER title is served 2/2
            # while this row printed `grafana does NOT serve all 2 of them` — and `names` is
            # the TITLE group, so the file it was really about was never named.
            group = {dest for _name, _title, _uid, dest in files}
            repeated = sorted({uid for _name, _title, uid, _dest in files
                               if isinstance(uid, str)
                               and len([d for d in claimed[uid] if d in group]) > 1
                               and _grafana_stored_uid(uid) is not None})
            trimmed = sorted({uid for _name, _title, uid, _dest in files
                              if isinstance(uid, str)
                              and len([d for d in claimed[uid] if d in group]) == 1
                              and len([d for d, _src in held.get(_grafana_stored_uid(uid), ())
                                       if d in group]) > 1})
            # AND THE `SILENTLY` HALF IS A CLAIM ABOUT THE **WHOLE LOG**, WHERE `trimmed` IS A
            # QUESTION ABOUT **THIS GROUP** — so it has to be re-asked at the log's own scope.
            # The two spellings in the group differ, so the dedupe does not fire FOR THIS PAIR;
            # a file delivered OUTSIDE the group repeating one of them makes it fire on that
            # spelling anyway, and the operator was told there was nothing to grep for.
            # `claimed` is GLOBAL — the engine's dedupe is, and the scoping above deliberately
            # moved the question and not the tracker — so its own predicate is already in hand.
            # Measured, two containers on the pinned image, two providers in ONE container with
            # every title unique and no spelling crossing a provider
            # (`critic-9ffc-r8-crossgroup-repeat` C1/C2, re-run unedited at this round's hands
            # in `builder-9ffc-r9-engine-recheck.log`): the group's spelling repeated outside it
            # is `the same UID is used more than once` uid=<that spelling> times=2 with the
            # lockout, and C3 is the ANTI-VACUITY CONTROL in that same container — the identical
            # tree with the outsider on an unrelated address is genuinely silent.
            # THE EMPTY SPELLING CANNOT REACH THIS LIST, so it needs no `and spelling` fence of
            # its own: `trimmed` is reached only through `held`, which never keys on None, and
            # `_grafana_stored_uid("")` is None (mem-1785599396-d436 — that class is the one the
            # engine skips at the dedupe, so a fence-free `claimed` lookup here cannot name it).
            loud_trim = sorted({u for u in trimmed if len(claimed[u]) > 1})
            # AND THE LOUD SPELLING IS **THIS GROUP'S OWN**, WHICH IS WHY THE CLAUSE DEFERS TO
            # THE `shared` PARAGRAPH INSTEAD OF ATTRIBUTING THE COLLISION AWAY. Round 9 closed
            # it with "the OTHER claimant's doing and not this pair's, so the line names a uid
            # these two files do not lose a file to", and that is false by construction on both
            # halves: `loud_trim ⊆ trimmed` is built out of THIS group's delivered uids, so the
            # spelling the engine names is always carried by one of the files named above, and
            # `u in trimmed` forces `_grafana_stored_uid(u)` non-None, so an outsider delivering
            # `u` is stored at THIS group's address. Measured, three providers in one container
            # on the pinned image with the store read back over the HTTP API
            # (`critic-9ffc-r9-loud-uid-is-the-address` qa/qb, re-run unedited at this round's
            # hands in `builder-9ffc-r10-review-harness-recheck.log`): served 1/3 and the
            # SURVIVOR IS THE OUTSIDER — the files the verdict named held 0 of their 2, at the
            # uid the log line names, while `shared` two sentences later said `So a file IS
            # lost` about that same address in that same verdict.
            # THE DEFERRAL CANNOT DANGLE: `loud_trim` non-empty ⟹ `shared` non-empty. Both
            # trackers are filled in ONE loop past ONE fence, so a claimant of the spelling is a
            # claimant of the address, and it is outside the group by the in-group count of 1
            # that put `u` in `trimmed`. Any round that moves the `shared` paragraph out of this
            # verdict has to take this sentence's last clause with it (red-9ffc R14a).
            # THE THIRD LIST IS A DIFFERENT FACT AND GETS ITS OWN SENTENCE, because the
            # engine does not answer it either. `ha` and `hb` are the SAME three (uid, title)
            # triples with the FILE NAMES swapped and are served 2/2 and 1/2, and `hc`
            # answered 1/2 then 2/2 on IDENTICAL BYTES in two containers (H5/H6) — which of
            # two colliding files the provisioner keeps is not stable, so `serves all` would
            # be as false here as `does NOT` was. A file IS lost; what this delivery does not
            # decide is which SIDE of the group boundary loses it. `held` is the whole
            # address, so it catches both routes at once, and it never keys on None — the
            # no-address class (R11) has nothing to collide on and cannot reach this list.
            shared = sorted({uid for _name, _title, uid, _dest in files
                             if isinstance(uid, str)
                             and [d for d, _src in held.get(_grafana_stored_uid(uid), ())
                                  if d not in group]})
            # PRINTED AS `src -> the file it is delivered as`, because the src basename is
            # exactly what may NOT be unique — the identity above is the dest for that
            # reason, and an outside claimant sharing a group member's basename would
            # otherwise be named with a string already in `names`.
            #
            # AND THE DEST HALF IS THE DEST **RELATIVE TO THE DASHBOARDS DIRECTORY**, WHICH IS
            # THE COORDINATE THE GROUP KEY IS BUILT ON. The clause below says this file is
            # delivered OUTSIDE this title group; the key is `(folder, saved)` and with
            # `foldersFromFilesStructure: true` the SUBDIRECTORY IS THE FOLDER, so the folder
            # is what puts it outside — and `d.rsplit("/", 1)[-1]` was the operation that
            # deleted it. The sentence asserted which side of a boundary a file was on and
            # printed a name with that boundary's coordinate cut off. TWO FAILURES, ONE
            # STRING, measured whole-guard over tempdir trees (`red-9ffc-r12` E1/E2, the same
            # pair the review measured in `critic-9ffc-r11-outside-identity` D1/D2): an
            # outsider in `team-b/`, delivered from a src carrying a group member's basename
            # onto that member's dest basename, printed `grafana-homelab-dashboard.json ->
            # homelab.json` — BOTH halves strings this verdict already prints as this group's
            # own, which is the confusion this print exists to prevent; and `outside` is a
            # SET, so TWO claimants in two folders printed ONE entry while the verdict still
            # closed `So a file IS lost — fix the uid on whichever side should not own it`.
            # THE TRUNCATION WAS THEREFORE ALSO THE ARITY: what separates two such claimants
            # is exactly the field it removed (E2 against E3, where distinct dest basenames
            # printed two entries all along). `d` is the loop variable one character away.
            #
            # RELATIVE AND NOT WHOLE: `foldersFromFilesStructure` is `false` in this repo, so
            # over the tree as delivered there is no folder at all, and `d` printed whole
            # would put the machine's filesystem layout — identical on every line — in front
            # of the operator on every tree this role actually ships (E4). `folder` above is
            # cut the same way, at the `titles` key.
            outside = sorted({f"{src_name} -> {d[len(DASHBOARDS_DIR):].strip('/')}"
                              for _name, _title, uid, _dest in files
                              if isinstance(uid, str)
                              for d, src_name in held.get(_grafana_stored_uid(uid), ())
                              if d not in group})
            if repeated or trimmed:
                serving = (
                    f"grafana does NOT serve all {len(files)} of them either."
                    + (f" The delivered uid(s) {repeated!r} are carried by more than one "
                       "delivered dashboard, so it keeps ONE per repeated spelling; that half "
                       "belongs to the row above, and for THAT one the engine does print `the "
                       "same UID is used more than once`." if repeated else "")
                    + ((f" The delivered uid(s) {trimmed!r} trim to a uid another delivered "
                        "dashboard is stored under, so it keeps ONE file there too")
                       + (" — SILENTLY: "
                          "the engine prints no uid line of any kind for this half, because its "
                          "dedupe reads the spelling AS DELIVERED and these differ. That is the "
                          "row above's `keeps ONE file, silently` branch, and over this tree the "
                          "guard's own sentence is all the operator gets "
                          "(critic-9ffc-r5-trim-uid-under-one-title C3/C4/C7)." if not loud_trim
                          else f". AND THIS HALF IS NOT SILENT: {loud_trim!r} is delivered more "
                          "than once across the WHOLE delivery, so the engine's dedupe DOES fire "
                          "on that spelling and prints `the same UID is used more than once` "
                          "naming it — go read that line too. THAT SPELLING IS ONE OF THESE "
                          "FILES' OWN: the duplicate is a file named above PLUS at least one "
                          "delivered OUTSIDE this group, and a file carrying a spelling that "
                          "trims onto this group's address is stored AT that address, so the "
                          "warning and this collision are ONE thing and not two. WHICH file at "
                          "that address the store keeps is what the paragraph below says this "
                          "delivery does not settle (critic-9ffc-r9-loud-uid-is-the-address "
                          "qa/qb, served 1/3 with the SURVIVOR the OUTSIDER — the files named "
                          "there held 0 of their 2, at the very uid the log line names — and qc "
                          "is that same tree with the claimant elsewhere, where the engine is "
                          "silent and the sentence above it is the true one).") if trimmed else ""))
            elif shared:
                # NEITHER OF THE OTHER TWO SENTENCES' NEEDLES APPEARS HERE, deliberately.
                # `grafana serves all N of them` and `does NOT serve all N of them` are what
                # every harness in this thread greps for, so a third sentence that embedded
                # either would read as one of them to a substring scorer — my own R12a
                # asserted exactly that and caught the first draft of this line.
                serving = (f"whether all {len(files)} of them reach grafana's store is NOT "
                           "decided by this delivery.")
            else:
                serving = (
                    f"grafana serves all {len(files)} of them, so nothing looks wrong on the day "
                    "it ships and the damage is entirely in the future: every later edit to any "
                    "of them silently stops being applied.")
            if shared:
                # WHAT IS SAID ABOUT THE OUTSIDE CLAIMANT IS WHAT `held` HOLDS, AND `held` IS
                # `(dest, src.name)`. Until this round this sentence volunteered `delivered
                # under a DIFFERENT title` — the one fact about that file the operator would
                # search on, and nothing in this row ever compares its title to the group's.
                # It is not merely unasked, it is FALSE on a live class: the group key is
                # `(folder, saved)`, so with `foldersFromFilesStructure: true` the
                # subdirectory IS the folder and a file carrying the group's OWN title in
                # ANOTHER subdirectory is OUTSIDE the group and can claim its address.
                # Measured at the guard (red-9ffc-r11 B1/B2/B3): that tree and the tree with
                # the claimant under its own title print BYTE-IDENTICAL verdicts, so no
                # conditional could rescue the claim — the row would have to read a title it
                # never opens. And it is not a paper tree: two providers in ONE container on
                # the pinned image (`critic-9ffc-r10-shared-paragraph` pf/pg, 13/13) take the
                # LOCKOUT with the title line counting `times=2` for the FOLDER only, the
                # dedupe firing on the shared spelling, and the ONE file served at the
                # contested address IS the outsider whose title this used to call different.
                # `d not in group` is what was actually asked, so it is what is now printed.
                #
                # AND THE PRONOUN COMES FROM `len(files)` LIKE EVERY OTHER ONE IN THIS
                # VERDICT. `these two files` was round 9's defect one paragraph up; the same
                # clause survived here through round 10 because its carrier greped for two
                # literal spellings and this was a third (red-9ffc-r11 A1/A3 scan the whole
                # paragraph and resolve every count-shaped phrase against `len(files)`; A2 is
                # the pair control, where a pair-shaped pronoun is the correct English).
                serving += (f" The delivered uid(s) {shared!r} are stored at an address ALSO "
                            f"claimed by {outside} — delivered OUTSIDE this title group, so "
                            f"the {len(files)} files named here are not the whole collision. "
                            "The engine keeps ONE file per address and WHICH ONE is not "
                            "something this delivery settles: the same three (uid, title) "
                            "triples with the file names swapped are served 2/2 and 1/2, and "
                            "one tree answered 1/2 and then 2/2 on identical bytes in two "
                            "containers (critic-9ffc-r7-crossgroup-serving H4/H5/H6). So a "
                            "file IS lost — fix the uid on whichever side should not own it.")
            bad.append(f"dashboard title {delivered} is delivered by {names} into one "
                       f"folder ({folder or 'General'}){decoded} — grafana disables the "
                       "WHOLE provider's writes: every dashboard it owns stops being updated, "
                       f"the same blast radius a repeated uid causes. {serving} AND THE ENGINE "
                       "NAMES THE TITLE, NOT THESE FILES: grep the provisioning log for "
                       "`dashboard title is not unique in folder` — one line carrying the "
                       f"title verbatim, the `folderID`, `times={len(files)}` and the "
                       "provider, printed immediately above the bare `has no database write "
                       "permissions because of duplicates`. The mapping from that title back "
                       f"to these {len(files)} FILES is the one thing it does not give "
                       "(red-9ffc-r5-title-line W1/W2/W6/W7, "
                       "critic-9ffc-r4-unfiltered-log U1/U2)")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: {len(inventory)} delivered dashboard(s) carry "
          f"{len(titles)} distinct title(s) in {len({f for f, _t in titles})} folder(s) "
          f"(problems={bad})")
    return ok


def test_pve_panels_name_series_the_exporter_declares() -> bool:
    """Every `pve_*` name in a delivered dashboard must be one the exporter emits.

    THE 4B FAILURE THIS FILE CAN ACTUALLY SEE. The rest of this guard proves the
    JSON parses, is delivered, is readable and points at a datasource that
    resolves — and every one of those can be green over a dashboard whose panels
    all read "No data" because a series name is a near-miss. `pve_up` is the only
    `pve_*` series this repo had PINNED before Step 4b (gate 2b's acceptance);
    everything else a panel names is a claim about an exporter no agent here can
    query.

    So the names are checked against a list read out of the pinned image itself
    — see `PVE_EXPORTER_SERIES` for the provenance and for the half of the claim
    this does NOT make (that the live API populates a given family).

    SCANNED OVER THE RAW TEXT, not over the keys this reader happens to model. A
    series name reaches Prometheus from a panel `expr`, an annotation `expr`, a
    template variable's `query` and its `definition`, and Grafana keeps adding
    places; a reader that enumerated them would be silently blind to the next
    one. Any `pve_…` token ANYWHERE in a delivered dashboard has to be a real
    series. The price is that these JSONs may not use a `pve_…` token as prose in
    a title or description, which is loud, immediate, and the direction that
    cannot ship a panel querying a series that does not exist.

    THE TOKENISER IS THE SCOPE, so it is written against the grammar of the thing
    being named and not against the names that happen to exist today. A Prometheus
    metric name is `[a-zA-Z_:][a-zA-Z0-9_:]*`: upper case is legal, and so is `:`.
    A near-miss the pattern cannot FORM is not a rejected name, it is an invisible
    one — the allow-list is never reached and the check is green over a panel that
    will read "No data". Measured, on the real dashboards, against the guard as it
    is on disk (`logs/rework-step04b-r6-pve-token-case.py`, 15/15 in all three
    modes): under `\bpve_[a-z0-9_]+\b` the token `pve_upTime_seconds` vanishes
    rather than truncating and the guard says PASS 13/13; widening only the tail
    class leaves `PVE_up` and `Pve_up` equally invisible; and where a `:` splits a
    name whose head IS a declared family — `pve_up:rate5m`, a recording rule
    nothing here defines — the truncated `pve_up` is ACCEPTED, so the colon has to
    be inside the class for the same reason the capitals do. Hence
    `[Pp][Vv][Ee]_[A-Za-z0-9_:]+`. The real tree names the IDENTICAL 12 tokens
    under every one of those patterns, so the widening costs nothing here (DEC-077).

    The price is unchanged in KIND: prose already reddened in lower case and now
    reddens in `PVE_` case too. The bound it does NOT close: `pve_` EMBEDDED after
    a word char (`node_pve_up`) is a different namespace and stays invisible, as
    does every non-`pve_` family a panel might name — closing that needs a live
    Prometheus, which this offline gate does not have.

    Anti-vacuity: the role delivers a PVE dashboard, so an inventory naming ZERO
    `pve_*` series FAILS. Otherwise deleting the dashboard would make this check
    pass by having nothing to check.
    """
    body = _read(TASKS)
    if body is None:
        print("FAIL: pve panels name real series (tasks/main.yml unreadable)")
        return False
    inventory = _delivered_dashboards(body)
    if not inventory:
        print("FAIL: pve panels name real series (no dashboard is delivered)")
        return False
    bad, seen = [], {}
    for name, src, _dest, rendered in inventory:
        if src is None:
            bad.append(f"{name!r}: delivered with no `src:` — nothing on disk to scan")
            continue
        raw = _read(src)
        if raw is None:
            bad.append(f"{name!r}: src {src} "
                       f"{_unreadable(src, provisioned=True, rendered=rendered)}")
            continue
        for series in sorted(set(re.findall(r"\b[Pp][Vv][Ee]_[A-Za-z0-9_:]+\b", raw))):
            seen.setdefault(series, []).append(src.name)
            if series not in PVE_EXPORTER_SERIES:
                bad.append(f"{src.name}: {series!r} is not one of the {len(PVE_EXPORTER_SERIES)} "
                           "families prompve/prometheus-pve-exporter:3.9.0 declares")
    if not seen:
        bad.append("no delivered dashboard names any pve_* series at all — the Proxmox "
                   "dashboard Step 4b delivers is missing, or its panels query nowhere")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: {len(seen)} distinct pve_* series named across "
          f"{len(inventory)} delivered dashboard(s) are all declared by the pinned exporter "
          f"(problems={bad})")
    return ok


def test_plex_panels_name_series_the_exporter_declares() -> bool:
    """Every `plex_*` name in a delivered dashboard must be one the exporter emits.

    THE 4C TWIN OF THE `pve_*` ROW, and it exists for the same reason: the twelve
    checks above are all green over a dashboard whose stream panels read "No
    data" because a name is a near-miss. `plex_media_count` and
    `plex_sessions_count` are the only two this repo had PINNED (Step 3b's
    acceptance, task-1785370581-de17); the other five a composite might name are
    claims about an exporter no agent here can query, so they are checked against
    a vocabulary read out of the pinned image — see `PLEX_EXPORTER_SERIES` for
    the provenance, for the interpolated-symbol wrinkle that makes this list rest
    on `compose.yml.j2`'s `METRICS_PREFIX=plex`, and for the half of the claim it
    does NOT make.

    THE TOKENISER IS WRITTEN AGAINST THE GRAMMAR, not against the seven names
    that exist today — DEC-077's lesson, taken rather than re-learned. A
    Prometheus metric name is `[a-zA-Z_:][a-zA-Z0-9_:]*`, so upper case and `:`
    are legal, and a near-miss the pattern cannot FORM is not a rejected name but
    an INVISIBLE one: the allow-list is never reached and the check is green over
    a panel that will never populate. Hence `[Pp][Ll][Ee][Xx]_[A-Za-z0-9_:]+`,
    which forms `PLEX_up`, `plex_upTime`, and `plex_up:rate5m` alike.

    THE PRICE IS THE SAME ONE THE `pve_*` ROW CHARGES AND IT IS DELIBERATE: these
    JSONs may not use an UNDECLARED `plex_…` token as prose in a title or
    description. The price is on the VOCABULARY, not on the location — measured
    both ways (`logs/red-step04c-mutations.log`), because the first spelling of
    this paragraph said "a `plex_…` token in prose reddens" and that is false:
    row C5 writes the real `plex_up` into a panel title and stays GREEN, while
    row B14 writes `plex_heartbeat` into the same slot and reddens. So the rule
    to follow when writing a title is "name a real series or name none", and the
    honest paragraph about what is unverified belongs by the delivery task in
    `tasks/main.yml`, which nothing here scans, and in the scratchpad.

    THE BOUND: `plex@file` is NOT a `plex_` token (no underscore) and is not
    claimed here — the traefik rows below own it. Neither is a family whose name
    does not start `plex_`, nor `plex_` embedded after a word char; closing that
    needs a live Prometheus, which this offline gate does not have.

    Anti-vacuity: the role delivers a dashboard whose whole subject is the Plex
    exporter, so an inventory naming ZERO `plex_*` series FAILS. Otherwise
    deleting that dashboard would make this check pass by having nothing to check.
    """
    body = _read(TASKS)
    if body is None:
        print("FAIL: plex panels name real series (tasks/main.yml unreadable)")
        return False
    inventory = _delivered_dashboards(body)
    if not inventory:
        print("FAIL: plex panels name real series (no dashboard is delivered)")
        return False
    docs, bad = _delivered_dashboard_documents(body)
    seen = {}
    for label, doc in docs:
        for _where, text in _json_strings(doc):
            for series in sorted(set(re.findall(r"\b[Pp][Ll][Ee][Xx]_[A-Za-z0-9_:]+\b", text))):
                seen.setdefault(series, []).append(label)
                if series not in PLEX_EXPORTER_SERIES:
                    bad.append(f"{label}: {series!r} is not one of the {len(PLEX_EXPORTER_SERIES)} "
                               "families ghcr.io/axsuul/plex-media-server-exporter:2.1.0 declares")
    if not seen:
        bad.append("no delivered dashboard names any plex_* series at all — the composite "
                   "Plex dashboard Step 4c delivers is missing, or its panels query nowhere")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: {len(seen)} distinct plex_* series named across "
          f"{len(inventory)} delivered dashboard(s) are all declared by the pinned exporter "
          f"(problems={bad})")
    return ok


def test_delivered_dashboard_queries_are_readable() -> bool:
    """Every prometheus query a delivered dashboard declares must sit in a field
    the three PromQL rows below actually read.

    THIS ROW EXISTS BECAUSE THE ROW AFTER IT WAS NARROWED. Until round 11 those
    three read EVERY string in the JSON, which was wrong in the loud direction —
    a `description` documenting a panel's own series was refused as if it were the
    query — and the fix is to read the fields where a dashboard DECLARES a query
    (`_dashboard_query_strings`). But a narrowing pays in the SILENT direction: a
    query that moves to a key this file does not know is not refused, it is simply
    never examined, and three rows finding nothing to check print the same OK as
    three rows finding nothing wrong. So the difference between "the slots a query
    lives in" (`_dashboard_query_carriers`) and "the queries this file can read"
    is reported here, by the file itself, rather than being left for a reviewer to
    notice.

    WHAT IS NOT ASKED FOR, and why that is not the same hole. A target whose
    datasource TYPE is declared and is not `prometheus` carries no PromQL, so no
    `expr` is demanded of it — an ordinary Grafana export's built-in annotation
    (`-- Grafana --`) and any future mixed-datasource panel stay green. An
    UNDECLARED type is treated as prometheus, because both delivered dashboards
    are, and because the fail-closed direction of that guess is a refusal a
    reader can answer in one line. THAT THE DECLARED TYPE CAN BE BELIEVED IS NOT
    THIS ROW'S OWN CLAIM, and it is not free either: the type routes nothing —
    Grafana sends the query to the datasource the `uid` names whatever the type
    says (calibration R2-R5 of `logs/calibration-step05b-type-vs-uid-routing.py`)
    — so a type that disagrees with its uid would exempt a carrier whose PromQL
    still reaches Prometheus. `test_delivered_dashboard_datasource_types_agree_
    with_the_provisioned_uid` is what forbids that disagreement, and the two
    rows are read together or neither is sound. A variable whose type is a declared non-query
    one (`GRAFANA_NON_QUERY_VARIABLE_TYPES`) is likewise not a query carrier — its
    `query` is a value list, not an expression.

    Anti-vacuity, and it is the reader's own: ZERO readable queries across the
    delivered dashboards FAILS. Otherwise a `_dashboard_query_strings` that
    returned nothing at all — the exact regression this narrowing risks — would
    leave all three rows below vacuously green and this row green beside them.
    """
    body = _read(TASKS)
    if body is None:
        print("FAIL: dashboard queries are readable (tasks/main.yml unreadable)")
        return False
    if not _delivered_dashboards(body):
        print("FAIL: dashboard queries are readable (no dashboard is delivered)")
        return False
    docs, bad = _delivered_dashboard_documents(body)
    readable = other_datasource = 0
    for label, doc in docs:
        found = {where for where, _text in _dashboard_query_strings(doc)}
        readable += len(found)
        for where, kind, node, ds_type in _dashboard_query_carriers(doc):
            if ds_type is not None and ds_type != GRAFANA_PROMETHEUS_DATASOURCE_TYPE:
                other_datasource += 1
                continue
            if kind == "variable" and node.get("type") in GRAFANA_NON_QUERY_VARIABLE_TYPES:
                continue
            if any(read.startswith(where) for read in found):
                continue
            bad.append(f"{label}{where[1:]}: this {kind} declares a query this check cannot "
                       f"read — its keys are {sorted(node)}, and the three PromQL rows read "
                       f"`{GRAFANA_TARGET_EXPR_KEY}` (any depth) and a `"
                       f"{GRAFANA_QUERY_VARIABLE_TYPE}` variable's "
                       f"{list(GRAFANA_VARIABLE_QUERY_KEYS)}, so nothing below examines it")
    if not readable:
        bad.append("no delivered dashboard declares a single query in a field this file reads — "
                   "the three PromQL rows below are all vacuous")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: {readable} declared quer(ies) across {len(docs)} delivered "
          f"dashboard(s) sit where the PromQL rows read them "
          f"({other_datasource} carrier(s) on another datasource) (problems={bad})")
    return ok


def test_dashboard_variables_are_declared_where_they_are_used() -> bool:
    """Every `$name` a delivered dashboard interpolates must be declared in that
    dashboard's own templating.list.

    STEP 4'S OWN TEST REQUIREMENT, WHICH NOTHING ELSE HERE ANSWERS: "verify that
    the Proxmox dashboard's container drop-down correctly lists CT 110 (Plex) and
    CT 111 (docker-host)". Every panel of that dashboard scopes to `{id="$guest"}`
    — thirteen targets across nine panels — so if the variable `guest` stops
    existing, the drop-down is gone AND every panel queries the literal string
    `$guest`, which matches no series. Measured by the Step 4b Finalizer's
    battery against the guard as it then stood: deleting `templating.list`
    outright is GREEN 13/13 (F7), and the realistic version — renaming the
    variable and leaving the thirteen references dangling (F7b) — is GREEN too.
    The rest of this file proves the JSON parses, is delivered, is readable,
    resolves its datasource and names real `pve_*` families, and NOT ONE of those
    is falsified by a variable that no longer exists.

    ROUND 11 OF STEP 4C ENUMERATES `templating.list` ALREADY, and it is worth
    saying why that is not this. It taught the guard to read a query variable's
    `definition`/`query` as PromQL — "is this variable's own query readable". The
    question here is the other one, "is every name a panel USES declared", and no
    reader in this file compared an interpolated spelling to a declared one until
    this row. The declaration side is `_dashboard_variables`, the walk 4c already
    wrote, rather than a second copy of it (DEC-085).

    WHAT IS SCANNED, PART ONE: every string LEAF of the document
    (`_json_strings`), not the keys this file happens to model. A sigil-carrying
    variable reference reaches Grafana from a target `expr`, a panel `title`, a
    `legendFormat`, an annotation, a link URL, a threshold's text, and Grafana
    keeps adding places; the `pve_*` row's round-6 docstring made this argument
    for series names and it holds identically here. Walking the parsed VALUES
    rather than the raw bytes reaches the same set — none of those carriers is
    anything but a JSON string — and reads the text Grafana will read, after JSON
    unescaping, so a reference inside an escaped matcher (`{id=\\"$guest\\"}` on
    disk) is read as the `{id="$guest"}` it becomes.

    PART TWO, AND BREADTH DOES NOT REACH IT: the `repeat` clause, which names its
    variable BARE. Round 1 of this row listed a repeat clause among the carriers
    the string walk covers; it is not one, because there is no `$` in it for the
    grammar to match, and the review measured the consequence — rename the
    variable, fix all thirteen `$guest`, leave `repeat: guest` behind, and the
    panel silently stops repeating while this row prints OK.
    `_dashboard_repeat_clauses` reads it as the reference it is, and carries the
    argument for why that walk is scoped to `panels[]` instead of keyed at any
    depth like the `expr` one.

    WHICH SPELLINGS: all three of Grafana's, transcribed from the pinned image's
    own regex — see `_GRAFANA_INTERPOLATION`, including the `re.ASCII` that makes
    Python's `\\w` mean what JavaScript's does. `$guest`, `${guest}` and
    `[[guest]]`, each with its optional `:format` suffix, are one reference; a
    tokeniser that formed only the first would be silently blind to a dangling
    name written in either of the others, and this tree's thirteen references are
    all spelled the first way, so that blindness would look like success.

    WHICH NAMES ARE EXEMPT, ONE: the SET Grafana substitutes, sourced name by
    name out of the pinned image — see `GRAFANA_BUILT_IN_VARIABLES`, which
    carries the four sources and the two bounds. It is deliberately not the `__`
    PREFIX that stood here in round 1: `__` is the namespace an author may not
    declare, and Grafana leaves an unregistered `__` name LITERAL in the query,
    so exempting the whole prefix hides `$__guest` and `$__rate_intervall` — the
    same silent "No data" this row exists to catch, one namespace over. A set can
    go stale; when it does it refuses a real dashboard by name on the next
    `just test`, which is the loud direction.

    WHICH NAMES ARE EXEMPT, TWO — AND THIS ONE IS NOT GRAFANA'S AT ALL: an
    UNDECLARED reference to a capture group of the Go regexp `label_replace`
    expands, which is not a variable reference that failed. Grafana passing it
    through untouched is what makes the query work. THE GRAMMAR HAS TWO HALVES
    AND ROUND 3 SHIPPED ONE: `$1`/`${1}` name a group by POSITION, `$ct`/`${ct}`
    name one the same string declares with `(?P<ct>…)` or Go 1.22's `(?<ct>…)`.
    `_PROMQL_CAPTURE_GROUP` and `_PROMQL_GROUP_DECLARATION` carry those two
    calibrations — both engines, the alphabet, and the three measurements that
    decide where this fails closed: an undeclared name expands to EMPTY, so the
    named half is skipped only when the declaration sits in the same string; the
    match is exact, because Go reads `$ctx` as `${ctx}`; and a group declared in
    a matcher beside the call does not resolve in it, which is the one scope this
    per-string test gives up and says so.

    AND THE EXEMPTION TESTS THE SPELLING, NOT ONLY THE NAME — the seam round 4
    left, which is the one directly above read from the other side. A name is not
    a text: the WHICH SPELLINGS paragraph above has this row reading all seven of
    Grafana's texts precisely so a dangling name cannot hide in an unusual one,
    and Go
    reads TWO of them, so an exemption that fired on the name alone waved through
    `[[ct]]`, `${ct:raw}`, `${ct.tail}`, `${ct.tail:raw}` and `[[ct:csv]]` — five
    dead queries per working one, on both halves, the guard printing "skipped as
    PromQL capture groups" about text the TSDB stores verbatim.
    `_PROMQL_EXPAND_REFERENCE` carries the exhaustive enumeration (the tokeniser
    pinned by pattern and group count, all fourteen texts read by this file's own
    grammar first, then answered by the pinned Prometheus) and the accept side is
    the INTERSECTION of the two grammars rather than either one's names.

    AND IT READS THE REFERENCE WHERE GO READS IT, WHICH IS TWO CHARACTERS WIDER
    THAN THE TEXT — round 5's seam. An anchored test on the matched text cannot
    see either end of it: Grafana's alphabet is ASCII and Go's `extract()` keeps
    taking letters and digits past it, so `$ctß` is a reference to `ctß` that
    expands to NOTHING while the name looked up was `ct`; and Go spends `$$` as a
    literal `$` before it reads anything, so a `$$ct` whose tokeniser match
    begins at the second `$` is not a reference at all and draws the text `$ct`.
    A declared prefix exempting an undeclared full name is the wave-through
    direction, which is what this row exists to close, so both are asked in
    `_promql_capture_reference` — by the parity of the `$` run before the match,
    and by `_go_expand_absorbs` on the character after it. The alphabet is
    transcribed clause for clause from Go's own loop and measured per Unicode
    category, because the two obvious approximations (`\\w`, or "any non-ASCII")
    each refuse a query the pinned engine really runs.

    AND NEITHER OF THOSE TWO CHARACTERS IS NECESSARILY THIS FILE'S — round 6's
    seam, which is the sentence above read one grammar later. THE TWO GRAMMARS
    SHARE THE STRING IN SEQUENCE, NOT AT ONCE: `templateSrv.replace()` runs
    first, in one global pass, and Go reads its OUTPUT, in which every DECLARED
    or BUILT-IN reference has become its VALUE and every undeclared one has
    survived as its own text. So a substitution ABUTTING the match supplies the
    byte the boundary was read from — `$ct$guest` reaches Go as `$ctlxc/110` and
    draws `guest_name="/110"`, wrong rather than missing, and a value ending in
    `$` spends the match's own `$` from the other side. AND THE TWO ENDS ARE NOT
    AT THE SAME DISTANCE, because one of the two facts is a RUN: Go pairs `$`
    from the START of a maximal run, so on the left the neighbour that matters is
    the one ending at `start - run` — the match itself only when this file wrote
    no `$` in front of it. `_grafana_substituted_spans` is the list and
    `_promql_capture_reference` refuses both abutments, exactly scoped: the
    right-hand one only for the unbraced spelling, since `${ct}$guest` is a
    working query, and the left-hand one at the run's far edge, since
    `$guest-$$$ct` is one too. It is a refusal on an unknowable value, so it is
    fail-closed by choice — priced, with its one-character escape, in that
    predicate's own docstring, and measured on both engines in
    `logs/calibration-step05a-r7-substitution-boundary.py` and
    `logs/calibration-step05a-r8-parity-run-distance.py`.

    The exemption is not free of a duty either way: the count is printed on the
    line below, separately from the references actually checked, because round 1
    of this row was rejected for an exemption that inflated a number into looking
    like coverage.

    BOTH EXEMPTIONS SIT BEHIND THE DECLARED TEST, which is Grafana's own order
    and not a tidiness: `_evaluateVariableExpression` calls
    `getVariableAtIndex(variableName)` FIRST and only consults `macroRegistry`
    when that misses, so a dashboard that declares `timeFilter` — the one name in
    `GRAFANA_BUILT_IN_VARIABLES` an author is permitted to declare, since the
    rest are `__`-prefixed and the name validator refuses those — really does
    substitute its own variable. Round 4 tested the built-in set before the
    declaration and the capture group after it. There was no false GREEN in that
    (a declared `timeFilter` passes either way), but it filed one under "declared
    but never used" while the panel using it worked, and it made the ordering
    argument this docstring relies on true of only one of the two exemptions.

    THE DELETE DIRECTION IS DELIBERATELY NOT A FAILURE. A declared variable that
    nothing interpolates is reported in the line below and nothing more: 4c's
    composite legitimately declares none, a dashboard mid-edit may declare one
    before its panels use it, and reddening on it would make this guard fight
    ordinary authoring. The asymmetry is the point — a reference with no
    declaration renders broken, a declaration with no reference renders a
    drop-down nobody reads.

    Anti-vacuity: ZERO declarable references across the whole delivered inventory
    FAILS. The PVE dashboard's drop-down is the reason this row exists, so a tree
    that interpolates nothing has lost it. Neither a built-in nor a capture group
    counts towards the floor — both are exempt from the check, so a tree carrying
    only those would leave this row judging nothing while printing a number.

    AND IT IS A WHOLE-INVENTORY FLOOR, NOT A PER-DASHBOARD ONE — said here
    because an earlier draft of this paragraph claimed the clause made "the
    single edit that removes both the variable and its thirteen uses" visible,
    and it does not. `checked` is summed over every delivered dashboard, so ONE
    declared-and-used variable anywhere in the tree satisfies it: empty the PVE
    dashboard's templating.list AND rewrite its thirteen `$guest` to a literal —
    the drop-down gone outright, which is Step 4's Test Requirement gone — and
    this row stays GREEN as long as any other dashboard carries a variable of its
    own. That is the mutation this clause does not see, and it is one ordinary
    edit away, because 4c's composite or the next dashboard with a drop-down
    supplies the reference that satisfies the sum.

    WHY THE FLOOR IS NOT PER-DASHBOARD, and what stands in for it. A dashboard is
    allowed to declare and interpolate nothing — `grafana-plex-health-dashboard.json`
    does exactly that today — so "every dashboard interpolates something" would
    redden the delivered tree, which is AC (c)'s live case and not a defect. What
    is affordable is legibility: the per-dashboard `n ref/n declared` counts are
    printed on the line below, so a tree in which the PVE dashboard has gone to
    `0 ref/0 declared` reads as that on the gate's own output rather than hiding
    inside a total. Making it FAIL wants a pin on the PVE dashboard's own
    declaration — a claim about one dashboard's identity, which is a different
    row from this one's "every reference is declared where it is used", and is
    not smuggled in here.

    BOTH EXEMPTIONS APPLY TO INTERPOLATIONS AND NEITHER APPLIES TO A REPEAT
    CLAUSE, because the two carriers are resolved by different machinery. A
    `$name` goes through `templateSrv.replace`, whose fallback IS the built-in
    set, and it is a `$` sigil, which is what the PromQL capture group shares. A
    repeat clause goes through `sceneGraph.lookupVariable(variableName)`, which
    searches the declared variable set, knows nothing about macros, and is not a
    query at all — there is no `label_replace` in it. So `repeat: __from` does
    not repeat anything and neither does `repeat: 1`; both are reported here
    rather than waved through.

    THE ONE BOUND THIS ROW DECLARES RATHER THAN FIXES: a literal `$` in PROSE.
    "reads its token from $HOME/.pve-token" in a `description` is refused, and
    the refusal is not a bug in the tokeniser — a description IS interpolated at
    render (`VizPanel.getDescription` calls `this.interpolate(description)`,
    sourced in `logs/calibration-step05a-r3-capture-group.py`), so Grafana meets
    `$HOME` on exactly the path it meets a dangling `$guestt` on, takes exactly
    the same `return match` branch, and NOTHING in the document distinguishes
    the two. A row that let this through would have to stop reading descriptions
    and titles, where a real `$guest` is substituted and read by a human. So the
    refusal stands, in the loud direction: it names the file, the json path and
    the string, and the escape is one edit ("from the HOME directory's
    .pve-token"). This is a statement about a `$` followed by ASCII word
    characters in text meant for a reader; it is NOT a census of what else can
    carry that sigil into a dashboard string, and the digit case one paragraph up
    is the proof that such a claim would have been wrong.
    """
    body = _read(TASKS)
    if body is None:
        print("FAIL: dashboard variables are declared (tasks/main.yml unreadable)")
        return False
    if not _delivered_dashboards(body):
        print("FAIL: dashboard variables are declared (no dashboard is delivered)")
        return False
    docs, bad = _delivered_dashboard_documents(body)
    checked = builtin = captures = repeats = 0
    declared_count = 0
    unused = []
    per_dashboard = []
    for label, doc in docs:
        declared = {var["name"] for _where, var in _dashboard_variables(doc)
                    if isinstance(var.get("name"), str)}
        declared_count += len(declared)
        # The names Grafana REPLACES in this dashboard's strings — its own
        # declarations, plus the built-ins, which `updateIndex`/`macroRegistry`
        # resolve without being declared. Everything else survives into the query
        # as its own text, which is what makes the capture-group exemption
        # possible at all and what bounds it.
        substituted = declared | GRAFANA_BUILT_IN_VARIABLES
        here = checked
        used = set()
        for where, text in _json_strings(doc):
            groups = _promql_group_declarations(text)
            for name, spelling, span in _grafana_interpolations(text):
                if name not in declared:
                    if name in GRAFANA_BUILT_IN_VARIABLES:
                        builtin += 1
                        continue
                    if _promql_capture_reference(text, span, groups, substituted):
                        captures += 1
                        continue
                checked += 1
                used.add(name)
                if name not in declared:
                    bad.append(
                        f"{label}{where[1:]}: interpolates {spelling!r}, and {name!r} is not "
                        f"among the {sorted(declared)} this dashboard declares in its own "
                        "templating.list — Grafana substitutes nothing and the panel queries "
                        "the literal text")
        for where, name, _covers in _dashboard_repeat_clauses(doc):
            checked += 1
            repeats += 1
            used.add(name)
            if name not in declared:
                bad.append(
                    f"{label}{where[1:]}: repeats over {name!r}, and that is not among the "
                    f"{sorted(declared)} this dashboard declares in its own templating.list — a "
                    "repeat clause names its variable BARE, so nothing here carries a `$` to "
                    "make the break visible and the panel simply stops repeating")
        unused += [f"{label}:{name}" for name in sorted(declared - used)]
        per_dashboard.append(f"{label}={checked - here} ref/{len(declared)} declared")
    if not checked:
        bad.append("no delivered dashboard interpolates a single declarable variable — the "
                   "Proxmox dashboard's container drop-down (CT 110 / CT 111), which every one "
                   "of its panels scopes to, is gone")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: {checked} variable reference(s) ({repeats} of them a bare "
          f"repeat clause) across {len(docs)} delivered dashboard(s) name one of the "
          f"{declared_count} variable(s) declared in their own templating.list "
          f"[{', '.join(per_dashboard)}] ({builtin} "
          f"reference(s) to one of the {len(GRAFANA_BUILT_IN_VARIABLES)} sourced built-ins "
          f"exempt, {captures} skipped as PromQL capture groups, declared but never used: "
          f"{unused}) (problems={bad})")
    return ok


def test_pve_dashboard_declares_the_container_drop_down() -> bool:
    """The Proxmox dashboard must DECLARE the drop-down its Test Requirement names.

    STEP 4'S TEST REQUIREMENT, THE HALF THE ROW ABOVE CANNOT ANSWER FOR. That row
    claims "every `$name` a dashboard interpolates is declared in its own
    templating.list", which is true of this tree and STAYS true when the PVE
    dashboard's `templating.list` is emptied and its thirteen `$guest` rewritten
    to the literal `lxc/110` — the CT 110 / CT 111 drop-down gone outright — as
    long as any other dashboard carries a variable of its own, because that row's
    anti-vacuity floor sums `checked` over the WHOLE inventory. Measured as C1 of
    `logs/critic-step05a-r3-battery.py` and D1/D2 of
    `logs/red-step05a-rework-r4.py`; DEC-104 refused to smuggle the repair into
    that row, because a per-dashboard floor is FALSE of the delivered tree —
    `grafana-plex-health-dashboard.json` declares and interpolates nothing, which
    is legitimate — and the missing claim is about ONE dashboard's identity.

    SO THE POPULATION IS ONE DASHBOARD AND IT IS PINNED BY `uid`, not by the file
    it ships as: see `PVE_DASHBOARD_UID` for why the two ansible-side names are
    not identity, and for what happens when the pin matches nothing (this row
    FAILS, naming the uid it looked for and listing what the inventory did hold).
    That failure is the point of the pin, not an edge of it — "no such dashboard"
    treated as "nothing to check" is the same vacuity this row exists to close.

    AND THE PIN IS ON THE uid THE ENGINE STORES, NOT THE ONE ON DISK — the third
    row in this file keyed on that field, and the one an earlier round left
    behind when it taught the other two. `_grafana_stored_uid` is the same shared
    function `_grafana_short_uid_defect` and
    `test_delivered_dashboards_have_distinct_uids` ask: the provisioner strips
    `GRAFANA_SHORT_UID_TRIM` off both ends and SAVES the dashboard under what is
    left. Compared as delivered, `pve-overview` + one U+00A0 is a dashboard
    Grafana serves at `pve-overview` while this row says the Proxmox dashboard is
    not in the inventory at all — a false refusal on a served document, which is
    the class this file pays to avoid, and it reddens the WHOLE gate on a tree
    the engine is happy with. Measured at this row's own literal base, the stored
    uid read back over the HTTP API in the same run as both anti-vacuity controls
    (`logs/red-579d-r10.py` PART A `a-pve`, PART B end to end;
    `logs/critic-579d-r9-third-uid-row.py` PART A/C is the run that found it).
    A uid the engine addresses itself — a non-string one, or one that is only the
    trim class — is None here and matches nothing, which is correct: the pin is
    an address, and those dashboards are saved under a uuid no line in this repo
    can name.

    THREE CLAUSES, AND EACH ONE IS A DIFFERENT WAY FOR THE DROP-DOWN TO BE GONE
    WHILE EVERY OTHER ROW IN THIS FILE IS GREEN:

    AND THE FIRST CLAUSE IS MEASURED, NOT READ OFF THE DOCUMENTATION.
    `label_values` is not PromQL — Grafana's Prometheus datasource turns
    `label_values(<selector>, <label>)` into `GET
    /api/v1/label/<label>/values?match[]=<selector>` — so all three constants
    this row hardcodes were put through `prom/prometheus:v3.12.0` on a fixture
    carrying every `id` shape the exporter emits
    (`logs/calibration-step05d-label-values.py` / `.log`, 11/11): the delivered
    query returns the containers AND ONLY the containers (A1-A3), the scope
    dropped returns the node, the VM and the storage beside them (B1), the scope
    narrowed loses CT 111 (B2), and the wrong label returns an EMPTY list (B3) —
    a drop-down with nothing in it. Part C measures the harm the row exists to
    prevent, rather than asserting it: an unsubstituted `pve_up{id="$guest"}` is
    sent LITERALLY and selects nothing (C2), which is not an error and not an
    empty drop-down but a panel that is simply always blank.

      1. IT IS DECLARED, AND IT YIELDS THE CONTAINERS.
         `_pve_container_drop_down` reads the entry's own query as Grafana's
         `label_values(<selector>, <label>)` — the first reader in this file to
         form that call — and asks what the values would BE: the label yielded
         must be the one the panels match (`PVE_GUEST_LABEL`), the family must be
         one the pinned exporter emits, and the selector must admit both
         containers the Test Requirement names while refusing the node, QEMU and
         storage ids that share the label. A drop-down that has lost its `lxc/`
         scope still contains CT 110 and CT 111; it also contains the whole
         cluster, which is why the refuse direction is probed too. AND THE QUERY
         IS NOT THE ONLY KEY THAT DECIDES WHAT THE OPERATOR SEES: `regex` filters
         and rewrites the values BETWEEN the query and the drop-down, and `hide:
         2` renders no picker at all while every other clause here stays
         satisfied. Both are refused, both mechanisms are read out of the pinned
         Grafana rather than off the documentation, and the false side of each
         refusal is stated where it is made.
      2. THE PANELS SCOPE TO IT, AND WHAT IT HANDS THEM IS ONE CONTAINER. A
         declared drop-down nothing interpolates is a control that moves nothing
         — the exact state the row above deliberately does NOT fail on ("a
         declaration with no reference renders a drop-down nobody reads"), and on
         THIS dashboard it is the Test Requirement gone. So at least one label
         matcher on this dashboard must match `PVE_GUEST_LABEL` against the
         drop-down. AND THE SECOND HALF IS A RELATION, not a key: `includeAll`
         and `multi` let one variable substitute BOTH ids at once, as the regex
         alternation `PVE_ALL_ALTERNATION`, which a `=~` matcher reads exactly
         right and a `=` matcher does not read at all. So the pair (variable,
         operator) is checked, never the key alone — see
         `GRAFANA_VARIABLE_ALTERNATING_KEYS` for the chain and
         `_grafana_variable_alternates` for why this is not a clause of the
         classifier above. AND `allValue` IS THE SAME HALF ASKED OF EVERY
         OPERATOR, because it is not the same mechanism: that string REPLACES the
         substitution rather than widening it, and `formatValue` short-circuits
         before the datasource ever escapes it, so `=~` — the operator this row
         blesses for the two keys above — reads `.*` as the whole cluster. It
         lives inside the region the narrow rule accepts, which is why it is
         checked here and why round 3 could price it as unreachable and be wrong
         (`GRAFANA_VARIABLE_ALL_VALUE_KEY`). NONE OF THE THREE IS ASKED OF A
         PANEL THAT REPEATS OVER THE DROP-DOWN: that panel is handed one id
         before any of them is read, so refusing it would be refusing a working
         dashboard (`_panel_repeats_over`).
      3. NO PANEL PINS A CONTAINER BEHIND ITS BACK. A matcher on
         `PVE_GUEST_LABEL` that admits either container WITHOUT naming the
         drop-down is a panel that has stopped following it — `{id="lxc/110"}`,
         or the `{id=~"lxc/.*"}` that graphs all of them at once under a
         per-container title. This is what makes a PARTIAL rewrite visible:
         clause 2's floor of one would still be met by the twelve targets the
         edit missed.

    WHAT IS DELIBERATELY GREEN, because a guard that forbids a real edit is this
    repo's own recurring defect:

      * A CONSISTENT RENAME. `guest` → `ct` in the declaration and all thirteen
        references keeps the drop-down working, so the NAME is not the contract
        and this row does not pin one. The dangling half of that edit reddens in
        BOTH rows, for two different reasons.
      * A REWRITTEN QUERY that admits the same containers —
        `{id=~"lxc/(110|111)"}` — because the claim is about what the query
        YIELDS, not about the bytes on disk.
      * AN ORDINARY MULTI-SELECT DASHBOARD. `includeAll` or `multi` with every
        panel spelling `{id=~"$guest"}` is the standard Grafana idiom and the
        engine returns both containers for it (`logs/calibration-step05d-rework-
        r3-includeall.py` C2); `!~` returns the complement (C4). This is the
        whole reason the refusal is the pair and not the key, and E1/E2 of
        `logs/red-step05d-rework-r3.py` are what would redden if it ever became
        the key. WHAT IS LIVE INSIDE THAT ACCEPT REGION IS ROUND 4'S FINDING and
        is now refused: an `allValue` on the same variable (F1 above).
      * A PANEL THAT REPEATS OVER THE DROP-DOWN, under ANY of the three keys and
        under `=`. `repeat: "guest"` with the delivered `{id="$guest"}` is the
        canonical per-container idiom, each clone is handed one bare id, and
        round 3 reddened it — DEC-137's "the narrow rule has no false side" was
        false, and the correction is an exemption rather than a declared price
        because the panel is CORRECT, not merely tolerable (`_panel_repeats_over`,
        E1/E2/E5 of `logs/red-step05d-rework-r4.py`). The exemption is pinned to
        the variable the clause names and to the panel that carries it: a repeat
        over a second variable, or over one panel of thirteen, leaves the other
        twelve refused (E3/E4).
      * AND A ROW THAT REPEATS OVER IT, IN BOTH OF THE SAVE MODEL'S TWO
        SPELLINGS. Round 4 covered only the COLLAPSED one, where the children are
        nested under the row, and refused the EXPANDED one — which is what the
        row-repeat UI writes, is the same working dashboard, and is the escape
        this row's own refusal message offers an operator with nine panels
        (review F1, `logs/critic-step05d-r4-repeat.py` A1/A2 against A3). The
        children of an expanded row are its SIBLINGS: `_grafana_row_span` reads
        them and states its four bounds, all of them scored — the span starts
        after the row (B2), stops at the next row (B1), stays in its own
        `panels[]` list (B12) and is asked only of a row `Boolean(collapsed)`
        calls expanded (B5/B8/B9/B10) — in `logs/red-step05d-rework-r5.py`.
      * THE NODE PANELS. `pve_cpu_usage_ratio{id=~"node/.*"}` admits no container
        and is not asked to name the drop-down; a rule of "every `id` matcher
        interpolates it" would redden three delivered panels.
      * A NEW DASHBOARD DECLARING NOTHING, and every other dashboard in the
        inventory — this row speaks about one uid and says nothing about the rest.

    THE BOUNDS, DECLARED RATHER THAN DISCOVERED LATER:

      * A DROP-DOWN OVER A SYNTHESISED LABEL IS REFUSED, and one spelling of it
        is a genuine FALSE REFUSAL. `label_values(label_replace(pve_up, "n",
        "$0", "id", "lxc/.*"), n)` works: `label_replace` leaves non-matching
        series untouched, so no `n` label reaches the nodes, and `$0` keeps the
        WHOLE id, so the values are the `lxc/110` the panels match. This row
        refuses it, because the label it yields is not the label the panels
        compare against. The refusal is loud (`just test` exits 1, printing the
        query), the escape is to widen this reader, and it is the direction every
        unknown case in this file already pays. THE REASON IT IS A BOUND AND NOT
        A BUG is its near twin: the same query with `$1` yields the bare `110`
        and every panel reading it is EMPTY. Two spellings one character apart,
        opposite verdicts, and nothing in the document distinguishes them — so
        this row says what it can see. Both are scored, F1 and F2 of
        `logs/red-step05d-pve-dropdown.py`, so the price is on the record rather
        than in a reviewer's head.
      * A KEY OF THE ENTRY THAT NO ROUND HAS PRICED IS PRINTED, NOT FAILED, and
        that bound is the general repair this round owes. Three reviews in a row
        found a defect in a key nobody had looked at, each round answered the
        keys it was handed, and the entry has FOURTEEN of them, not the twelve
        two reviews called it (calibration D0). `GRAFANA_PVE_DROP_DOWN_KEYS_
        PRICED` is what has been examined and why; anything outside it appears on
        this row's output line, so the fourth finding of that class arrives on
        the gate rather than in the fourth review. It is printed and not failed
        because Grafana adds variable fields between releases and reddening for
        one that changes nothing is the false refusal this row pays to avoid.
      * A MATCHER BLOCK THIS FILE CANNOT PARSE IS COUNTED, NOT FAILED. `pve_up
        {$filter}` is the ordinary Grafana idiom of interpolating a matcher list,
        and `_promql_calls`' own docstring prices reddening it as the wrong trade.
        The count is printed, so a dashboard whose selectors have gone unreadable
        reads as that on the gate's output.
      * A SELECTOR WITH NO `id` MATCHER AT ALL is not read by clause 3: a
        cluster-wide panel on this dashboard is legitimate, and demanding an `id`
        matcher of every expression would forbid one. What that leaves uncovered
        is a panel that quietly graphs the whole cluster under a per-container
        title, and only 4d's operator sees it.
      * A PANEL THAT FOLLOWS A DIFFERENT VARIABLE IS NOT READ EITHER, and this
        one is FILED rather than declared closed, as `task-1785553255-bad2`
        (`code-assist:plex-monitoring:guard:pve-panels-follow-a-second-variable`).
        Clause 3 sees a container pinned as a LITERAL behind the drop-down's
        back; twelve of the thirteen panels repointed at a second, hardcoded
        `custom` variable listing `lxc/110,lxc/111` are neither literal nor
        naming the drop-down, and clause 2's floor of one is met by the target
        the edit missed — GREEN, measured as C4 of `logs/critic-step05d-battery.py`.
        It is not coded here because the honest shape of the fix is narrower than
        it first looks and belongs in its own round: refusing every `id` matcher
        that names a NON-drop-down variable would forbid a legitimate `$node`
        drop-down beside this one, so the rule has to be "a matcher on
        `PVE_GUEST_LABEL` naming a NON-`query` variable whose LITERAL values
        admit a Test Requirement container", which needs a reader this file does
        not have yet. A second QUERY variable that yields the containers is not
        the same hole — it is accepted as a drop-down, and two working container
        drop-downs are not a defect.
      * `allValue` IS REFUSED WHATEVER IT SAYS, and one spelling of it is a
        genuine FALSE REFUSAL — the same trade, for the same reason, as the
        `regex` refusal one clause up. `allValue: "lxc/.*"` under `=~` returns
        exactly the two containers (`logs/calibration-step05d-rework-r4-allvalue.
        py` C4) and is refused anyway, because deciding what an arbitrary string
        admits once `CustomAllValue` has bypassed every escape is the "cannot
        say" this file answers with a refusal everywhere else. The escape is one
        field of the variable editor, or a `repeat` clause; widening it later —
        by reading the string as clause 1 reads the query — is additive. Scored
        as D1 of `logs/red-step05d-rework-r4.py` so the price is on the record.
      * AND IT IS REFUSED WITH `includeAll` UNSET, which looks like over-reach and
        is not. The picker can only offer All under that key (r4 A3) and
        validation resets a stray All without it (A4) — but `updateFromUrl` calls
        `changeValueTo($__all)` with no such condition and its value SURVIVES
        that validation (A5/A6), and a link carrying the allValue string is a
        second door (A7). So a file with `allValue` alone is one shared URL from
        the harm; C3 of the round's RED scores exactly that state.
      * THE REPEAT EXEMPTION RESTS ON WHAT THE IDS ARE MADE OF. A clone's value
        goes through `prometheusSpecialRegexEscape`, and `lxc/110` is a fixed
        point of that character class while `lxc/1.0` would not be (r4 B2/B3). If
        the exporter ever emits an id carrying a regex metacharacter, a repeating
        panel on `=` stops being exempt-safe — stated here rather than left to be
        found.
      * `multi` IS REFUSED FOR A DEFECT THE FILE DOES NOT HAVE YET, and that is
        the declared price of clause 2's second half. `interpolateQueryExpr`
        returns `escapedValues[0]` for a single selection, so a `multi` drop-down
        with ONE container ticked interpolates the bare id exactly as today
        (calibration A6, engine C5) — the dashboard reads correctly until the
        operator ticks the second container, which is one click and no edit to
        any file. `includeAll` is the louder half of the same key class because
        it needs no click at all: All is the selection ON LOAD (A8/A9). Both are
        refused together; only the first is a state the tree could sit in
        looking fine, and it is scored as D3 of `logs/red-step05d-rework-r3.py`
        so the price is on the record rather than in a reviewer's head.
      * THE VALUES ARE PROBES, NOT AN INVENTORY. Whether the live cluster reports
        CT 110 and CT 111 at all is gate 2b's, and 4d's — the exporter has never
        run. This row answers what the delivered query ADMITS.
    """
    body = _read(TASKS)
    if body is None:
        print(f"FAIL: the dashboard delivered as uid {PVE_DASHBOARD_UID!r} declares the container "
              "drop-down (tasks/main.yml unreadable)")
        return False
    docs, bad = _delivered_dashboard_documents(body)
    mine = [(label, doc) for label, doc in docs
            if isinstance(doc, dict)
            and _grafana_stored_uid(doc.get("uid")) == PVE_DASHBOARD_UID]
    if not mine:
        bad.append(f"NO delivered dashboard carries the uid {PVE_DASHBOARD_UID!r} — the Proxmox "
                   f"dashboard is not in the inventory this row reads ({[l for l, _d in docs]}), "
                   "so either its delivery is gone, taking Step 4's CT 110 / CT 111 Test "
                   "Requirement with it, or the uid was edited and this pin now matches nothing")
    summary, unread = [], 0
    for label, doc in mine:
        queries = _promql_strings(doc)
        variable_paths = {where for where, _text in _dashboard_variable_queries(doc)}
        drop_downs, refused, alternating, unpriced, pastes_raw = [], [], {}, {}, {}
        repeats = _dashboard_repeat_clauses(doc)
        for base, var in _dashboard_variables(doc):
            name = var.get("name")
            if not isinstance(name, str):
                continue
            texts = [text for where, text in queries
                     if where.startswith(f"{base}.") and where in variable_paths]
            why = _pve_container_drop_down(var, texts)
            if why is None:
                drop_downs.append(name)
                keys = _grafana_variable_alternates(var)
                if keys:
                    alternating[name] = keys
                raw = _grafana_variable_all_value(var)
                if raw is not None:
                    pastes_raw[name] = raw
                rest = sorted(set(var) - GRAFANA_PVE_DROP_DOWN_KEYS_PRICED)
                if rest:
                    unpriced[name] = rest
            else:
                refused.append(f"{name!r} {why}")
        if not drop_downs:
            bad.append(f"{label}: declares no template variable yielding the containers Step 4's "
                       f"Test Requirement names — {refused or 'its templating.list is empty'}. "
                       "The container drop-down is the whole of that requirement")
        scoped = 0
        for where, text in queries:
            if where in variable_paths:
                continue
            for block, _start in _promql_matcher_blocks(text):
                matchers = _promql_matchers(block)
                if matchers is None:
                    unread += 1
                    continue
                # THE BLOCK IS THE SELECTOR, so both questions are asked of the
                # whole matcher list and not of one entry at a time: Prometheus
                # ANDs them, so `{id=~"lxc/.*", id="$guest"}` is scoped by its
                # second matcher however wide the first one reads, and an
                # entry-at-a-time reader would call that panel unscoped.
                on_guest = [m for m in matchers if m[0] == PVE_GUEST_LABEL]
                names_it = False
                for name, op, value in matchers:
                    named = sorted({ref for ref, _spelling, _span
                                    in _grafana_interpolations(value)} & set(drop_downs))
                    if not named:
                        continue
                    if name == PVE_GUEST_LABEL:
                        names_it = True
                        # CLAUSE 2'S SECOND HALF: naming the drop-down is not
                        # enough if what it interpolates is not ONE id. An All or
                        # multi selection arrives as the regex alternation
                        # `(lxc/110|lxc/111)`, which a pattern operator reads
                        # correctly and a literal one does not — so the question
                        # is asked of the (variable, operator) PAIR that this
                        # loop already holds, and never of the key alone.
                        #
                        # AND THE EXEMPTION IS ASKED FIRST, because a panel that
                        # REPEATS over the drop-down reads none of these keys: it
                        # is handed one id as a `LocalValueVariable` before any of
                        # them is consulted, so both refusals below would be
                        # refusing a panel that works (`_panel_repeats_over`).
                        for ref in named:
                            if _panel_repeats_over(repeats, where, ref):
                                continue
                            if ref in alternating and op not in PROMQL_REGEX_OPERATORS:
                                bad.append(
                                    f"{label}{where[1:]}: {block} compares the drop-down {ref!r} "
                                    f"with {op!r}, which reads the interpolated text as a LITERAL "
                                    f"string, and that variable declares {alternating[ref]} — with "
                                    "more than one container selected Grafana interpolates BOTH of "
                                    f"them, as the regex alternation {PVE_ALL_ALTERNATION!r}, "
                                    f"which no series' "
                                    f"{PVE_GUEST_LABEL!r} equals: this panel draws nothing under "
                                    "'=' and the WHOLE CLUSTER under '!='. Spell the matcher with "
                                    f"'=~', or clear {alternating[ref]}")
                            # AND THE `allValue` HALF IS ASKED OF EVERY OPERATOR,
                            # which is what makes it a different question from the
                            # one above rather than a fourth clause. With All
                            # selected that string REPLACES the substitution
                            # (`CustomAllValue`), and `formatValue` short-circuits
                            # before the datasource formatter — so nothing escapes
                            # it and nothing knows what operator it landed next
                            # to. `.*` under the `=~` this row otherwise blesses
                            # graphs the whole cluster on load.
                            if ref in pastes_raw:
                                bad.append(
                                    f"{label}{where[1:]}: {block} matches the drop-down {ref!r}, "
                                    f"and that variable declares allValue: {pastes_raw[ref]!r} — "
                                    "with All selected Grafana pastes that string into the query "
                                    "RAW, in place of any container id, without the datasource's "
                                    f"escaping and knowing nothing of this matcher's {op!r}: what "
                                    "the panel selects is whatever the string says, so '.*' draws "
                                    "the WHOLE CLUSTER under a per-container title while the "
                                    "picker still lists them. All is reachable from a link even "
                                    "with 'includeAll' unset. Clear allValue, or repeat the panel "
                                    "— or the row it sits under, collapsed or not — over the "
                                    "drop-down")
                    else:
                        bad.append(
                            f"{label}{where[1:]}: {block} matches the drop-down {named} "
                            f"against the label {name!r}, and the values it yields are "
                            f"{PVE_GUEST_LABEL!r} values — no series carries them there, so "
                            "every panel reading this selector is empty whatever is chosen")
                if names_it:
                    scoped += 1
                    continue
                if not on_guest:
                    continue
                admitted = []
                for probe in PVE_TEST_REQUIREMENT_GUESTS:
                    verdict = _pve_id_admits(on_guest, probe)
                    if isinstance(verdict, str):
                        bad.append(f"{label}{where[1:]}: {block} {verdict}")
                    elif verdict:
                        admitted.append(probe)
                if admitted:
                    bad.append(
                        f"{label}{where[1:]}: {block} selects {admitted} without naming the "
                        f"drop-down {drop_downs} — this panel has stopped following the "
                        "container the operator chose")
        if drop_downs and not scoped:
            bad.append(f"{label}: declares the drop-down {drop_downs} and NOT ONE selector on the "
                       f"dashboard matches {PVE_GUEST_LABEL!r} against it — the control renders "
                       "and moves nothing")
        summary.append(f"{label}: {drop_downs} scoped by {scoped} selector(s)"
                       + (f", refused {refused}" if refused else "")
                       + (f", keys NO ROUND HAS PRICED {unpriced}" if unpriced else ""))
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: the dashboard delivered as uid {PVE_DASHBOARD_UID!r} declares "
          f"a query variable yielding the containers Step 4's Test Requirement names "
          f"({', '.join(PVE_TEST_REQUIREMENT_GUESTS)}, and not "
          f"{', '.join(PVE_NON_CONTAINER_IDS)}), and its panels scope to it "
          f"[{'; '.join(summary) or 'no such dashboard'}] ({unread} matcher block(s) this gate "
          f"cannot read) (problems={bad})")
    return ok


def test_plex_latency_panels_select_the_file_provider_service() -> bool:
    """Every service-scoped Traefik selector must name `plex@file`.

    THE DEFECT THIS CATCHES IS A PANEL THAT IS NEVER EMPTY AND IS ALWAYS WRONG,
    which is why it needs a check rather than 4d's eye: Traefik's
    `traefik_service_*` families carry one series PER SERVICE, so
    `rate(traefik_service_request_duration_seconds_bucket[5m])` with no selector,
    or one naming `plex@docker`, renders a full graph of the whole proxy — every
    internal router, the dashboard, whoami — under a panel titled for Plex. An
    operator confirming "the panels populate" would tick it.

    BOTH HALVES OF THE VALUE ARE MEASURED, not read off the documentation
    (`logs/calibration-step04c-traefik-plex-series.log`, 7/7): the file-provider
    service came back labelled `plex@file` (R3) while a docker-provider control
    on the SAME proxy came back `whoami@docker` (R4). So `@file` is a statement
    about WHERE dynamic.yml.j2 defines the service, and moving that definition to
    a docker label — which is a real edit someone might make — renames the series
    out from under every panel here.

    THE SUBJECT IS FOUND BY ITS LITERAL NAME, SO A `__name__` REGEX IS INVISIBLE
    TO IT. `{__name__=~".*request_duration_seconds_bucket"}` with no `service`
    matcher never forms the token `traefik_service_…`, so this row is not asked
    about it and the panel graphs the whole proxy — PASS, measured 17/17 by the
    round-10 review. Round 10 taught this file that the name may live INSIDE the
    braces; this is the half of that class a literal-text scan cannot reach. It is
    filed as `task-1785516964-1b02` rather than coded because it is not a
    near-miss — nobody writes it by accident — and closing it means asking
    `_promql_matchers` whether a `__name__` REGEX could match the family, which is
    a different question from "does this text contain the name". The plex half of
    the same shape is loud only by accident (`{__name__=~"plex_media.*"}` reddens
    the `plex_*` NAME row); there is no traefik name row, and that asymmetry is
    the honest statement of what this row does not cover.

    SCOPED TO `traefik_service_*` AND NOT TO `traefik_*`, and the bound is
    measured rather than conceded: `traefik_entrypoint_request_duration_seconds`
    carries NO `service` label at all (R7), so there is nothing on it to select
    and a rule demanding one would forbid a legitimate future entrypoint panel.
    What that leaves uncovered is honest and stated: an entrypoint-family panel
    on this dashboard would show all traffic, and only 4d's operator sees it.

    STRICTER THAN THE RUNTIME IN ONE PLACE, deliberately: the matcher must be the
    exact equality `service="plex@file"`. A regex matcher that happens to select
    the same single series today (`service=~"plex.*"`) reddens, because it also
    selects whatever `plex`-prefixed service a later step adds, silently widening
    a panel that reads as scoped.

    THE BLOCK IS PARSED, NOT SEARCHED, and both directions of that were review
    findings. Until round 5 this asked whether the text `service="plex@file"`
    appeared ANYWHERE in the matcher block, which is not the same question: a
    neighbouring label name CONTAINS it, so `{exported_service="plex@file"}` was
    GREEN with `service` completely unconstrained, and so did a longer VALUE. That
    direction is the milder one and it is worth saying why — an equality on a label
    nothing carries selects NOTHING (calibration B18 returns no sample at all), so
    the panel is EMPTY and 4d's operator can see it, unlike the sibling row's typo,
    which restores a wrong number. The other direction was a false refusal: a
    quoted label name is legal in a matcher and IS the bare name
    (`{"service"="plex@file"}` — calibration A4), and the DELIVERED expression
    re-spelled that way was RED. `_promql_matchers` answers both.

    Anti-vacuity: an inventory naming ZERO `traefik_service_*` series FAILS —
    otherwise deleting the latency panels satisfies this by having nothing to
    check, which is precisely the state Step 1's whole deliverable was in before
    4c (its tuned buckets existed and NOTHING read them).
    """
    body = _read(TASKS)
    if body is None:
        print("FAIL: plex latency selectors (tasks/main.yml unreadable)")
        return False
    if not _delivered_dashboards(body):
        print("FAIL: plex latency selectors (no dashboard is delivered)")
        return False
    docs, bad = _delivered_dashboard_documents(body)
    selectors = 0
    want = f'{TRAEFIK_SERVICE_LABEL}="{TRAEFIK_PLEX_SERVICE}"'
    for label, doc in docs:
        for where, text in _promql_strings(doc):
            for m in re.finditer(r"\btraefik_service_[A-Za-z0-9_:]+", text):
                selector = _metric_selector(text, m.start(), m.end())
                if selector is None:
                    continue
                block, shown = selector
                selectors += 1
                matchers = _promql_matchers(block)
                if block is None:
                    bad.append(f"{label}{where[1:]}: {m.group(0)!r} carries NO label matcher — "
                               "that series exists once per service, so this panel graphs the "
                               "whole proxy under a Plex title")
                elif matchers is None:
                    bad.append(f"{label}{where[1:]}: {shown} is not a matcher list "
                               "this check can read — an unbalanced quote, an unquoted value, a "
                               "name with no operator or a string escape the PromQL lexer "
                               "rejects, each of which the Prometheus parser also refuses")
                elif not any(name == TRAEFIK_SERVICE_LABEL and op == "="
                             and value == TRAEFIK_PLEX_SERVICE for name, op, value in matchers):
                    bad.append(f"{label}{where[1:]}: {shown} carries no "
                               f"{want} matcher (measured row R3; a docker-provider service "
                               "would be `plex@docker`, and a matcher on a NEIGHBOURING label "
                               "name leaves `service` unconstrained)")
    if not selectors:
        bad.append("no delivered dashboard reads any traefik_service_* series — Step 1a tuned "
                   "the latency buckets and nothing shows them")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: {selectors} traefik_service_* selector(s) across "
          f"{len(docs)} delivered dashboard(s) all select {want} (problems={bad})")
    return ok


def test_plex_latency_panels_read_the_tuned_histogram_buckets() -> bool:
    """The latency panels must read the `_bucket` series Step 1a tuned.

    STEP 1A'S DELIVERABLE IS A BUCKET LADDER AND A LADDER IS ONLY REAL IF
    SOMETHING READS IT. `traefik_service_request_duration_seconds` is a histogram,
    so the same panel can be drawn three ways and only one of them touches the
    boundaries: `rate(…_sum)/rate(…_count)` is a mean and reads the ladder NOT AT
    ALL, `…_count` is a rate, and only `histogram_quantile()` over the `…_bucket`
    series interpolates between the `le` values. Measured
    (`logs/calibration-step04c-traefik-plex-series.log` R5): the 13 boundaries
    traefik.yml.j2 pins are exactly the `le` values that came back on the plex
    bucket series, so this family IS the one Step 1a tuned and the `_bucket`
    suffix IS how its resolution reaches a panel. A dashboard drawing the mean
    would populate, look right, and leave the whole of Step 1 unread — the plan's
    own Demo asks for latency, and the mean of a long-tailed latency
    distribution is the number the tuning existed to stop anyone quoting.

    THE THIRD CLAUSE IS THE SILENT ONE. `histogram_quantile` needs the `le` label
    to survive aggregation, so an aggregation that drops it yields a quantile
    computed over a series that no longer has boundaries. Grafana draws it. It is
    wrong and it is not empty, so 4d cannot catch it either.

    THAT CLAUSE IS WRITTEN OVER THE AGGREGATIONS APPLIED, NOT OVER THE CLAUSES
    WRITTEN, and the difference is a review finding this row already cost once
    (`mem-1785498725-78ea`). Round 1 iterated every `by (…)`/`without (…)` in the
    expression and demanded `le` survive it — so `sum by (code)` reddened and
    `without (le)` reddened, and `histogram_quantile(0.5, sum (rate(…_bucket[…])))`
    with NO modifier at all, which collapses `le` exactly as hard, matched no
    pattern, was never examined, and stayed GREEN. A bare aggregation is the more
    common spelling of this mistake, not the rarer one. So: every call applied to
    a span containing the bucket family is CLASSIFIED (see
    `PROMQL_AGGREGATION_OPERATORS`), and each aggregation must carry a modifier
    that KEEPS `le` — a `by (…)` naming it, or a `without (…)` not naming it.
    Absent modifier is the defect, not the default.

    "APPLIED" MEANS `le` IS STILL ALIVE AT THIS LEVEL, NOT "the bucket name is
    somewhere inside my parentheses" — and that distinction is the second review
    finding this row has cost. `histogram_quantile` CONSUMES `le`; what it
    returns is a plain latency, so `max(histogram_quantile(0.90, sum by (le)
    (rate(…))))` is a CORRECT expression and the engine returns the interpolated
    quantile for it (`logs/calibration-step04c-r3-promql-case.log` B4/B5). Round
    2 refused it, with a message about a label that no longer exists at that
    level. So the subject an aggregation is answerable for is one that reaches it
    UNCONSUMED — see `_promql_subject_reaches`, and note that a quantile stacked
    ABOVE an aggregation consumes nothing on its behalf, which is why
    `max(histogram_quantile(0.50, sum by (code) (…)))` is still RED.

    THE KEYWORDS ARE FOLDED AND THE LABEL NAMES ARE NOT, because that is what the
    parser does (calibration A1/A2/A4 against A5, B12). `sum BY (code)` is legal
    PromQL, collapses `le` identically, and was GREEN here for one character of
    case — the third finding, and the DEC-077 defect one layer up. `by (LE)`, on
    the other hand, groups by a label the series has never carried and stays RED.

    AND THE NAMES ARE UNQUOTED, because a quoted label name is legal in a
    grouping clause and IS the bare name (round-4 calibration A1/A2). That was
    the same defect one token class further out: `sum without ("le")` was GREEN
    here while the engine returned zero samples (B1), and the correct
    `sum by ("le")` was RED (B3). What the unquote must not do is documented and
    measured in `_promql_label_set` — an unbalanced quote and a name that only
    LOOKS like `le` both stay red.

    A SELECTION IS REFUSED HERE, AND FOR A DIFFERENT REASON THAN IT USED TO BE.
    `topk`/`bottomk` do NOT collapse labels — they hand the picked series back
    whole, `le` and `__name__` included (calibration C1-C4) — so the message this
    row printed, that `le` was collapsed, was factually false, which is a review
    finding this round paid. What they DO is drop the series they did not pick,
    and for a histogram the set of series IS the ladder: measured on a tie-free
    ladder, `topk(2, …)` in front of the quantile returns p20 = 0.3 against a
    true 0.06 (C9/C9'), and `bottomk(2, …)` drops `+Inf` and returns a NaN sample
    rather than an empty vector (C8/C8'). Drawn, and not a latency. So the
    refusal stays and the sentence changes.

    THE SIBLING ROW ACCEPTS THE SAME HEAD, AND THAT IS NOT THE ROUND-3
    DISAGREEMENT COMING BACK. `_promql_head_kind` still answers ONE question with
    ONE list — what does this head do to the series it is handed — and both rows
    read the same answer; what differs is the PRICE, because the subjects differ.
    `plex_media_count`'s series are independent (dropping one hides a library,
    which is what a top-N panel is asking for), while a bucket ladder's are a
    single measurement in parts. Round 3's defect was one QUESTION answered twice
    in two branches; this is one answer, priced where the harm is. A merge under
    a selection is still a merge and still red on both (battery R16/R17).

    THE ACCEPT SIDE IS MEASURED TOO, because a guard that forbids the real answer
    is the failure this repo has already had once. The engine itself was asked
    (`logs/calibration-step04c-r2-promql-aggregation.log`, rows B1-B8, real
    PromQL through `promtool test rules` over a synthetic ladder): a bare `sum`
    and a bare `avg` leave `histogram_quantile` with NOTHING (B2/B4) while the
    bare `sum` they wrap is itself a plausible single number (B3); and
    `without (code)` (B6), the TRAILING modifier spelling `sum (…) by (le)` (B7),
    and no aggregation at all (B8) are all CORRECT and stay green here.

    AN UNCLASSIFIED CALL HEAD IS RED, deliberately. The operator list cannot be
    complete — Prometheus adds functions, and two more aggregations already exist
    behind a feature flag (calibration row A4) — so the unknown case is the one
    that decides whether incompleteness is loud or silent. A refusal costs one
    line in `PROMQL_AGGREGATION_OPERATORS` or
    `PROMQL_LABEL_TRANSPARENT_CALLS` and prints the head it did not know;
    silent acceptance costs a quantile with no boundaries that nobody sees.

    WHAT THIS DOES NOT CLAIM: that the quantile is the RIGHT quantile, that the
    range is sensible, or that any sample exists. The last one is 4d's and it is
    blocked behind three operator gates that have never run.

    Anti-vacuity: at least one delivered dashboard must read the `_bucket`
    series. That is the clause AC (b)'s "replaced by an expression that does not
    read `_bucket`" mutation lands on.
    """
    body = _read(TASKS)
    if body is None:
        print("FAIL: plex latency reads the tuned buckets (tasks/main.yml unreadable)")
        return False
    if not _delivered_dashboards(body):
        print("FAIL: plex latency reads the tuned buckets (no dashboard is delivered)")
        return False
    docs, bad = _delivered_dashboard_documents(body)
    reads = 0
    for label, doc in docs:
        for where, text in _promql_strings(doc):
            if TRAEFIK_SERVICE_LATENCY_BUCKET not in text:
                continue
            reads += 1
            if "histogram_quantile(" not in text:
                bad.append(f"{label}{where[1:]}: reads {TRAEFIK_SERVICE_LATENCY_BUCKET} outside "
                           "histogram_quantile() — the le boundaries are counters, not a latency")
            if not re.search(r"\b(rate|irate|increase)\s*\(", text):
                bad.append(f"{label}{where[1:]}: reads the bucket counters raw, with no "
                           "rate()/irate()/increase() — a cumulative count, not a latency")
            calls = _promql_calls(text)
            consumers = [(start, end) for head, _, _, start, end in calls
                         if _promql_head_kind(head) == PROMQL_HEAD_QUANTILE]
            for head, clause, labels, start, end in calls:
                kind = _promql_head_kind(head)
                if kind == PROMQL_HEAD_QUANTILE:
                    continue
                if not _promql_subject_reaches(text, TRAEFIK_SERVICE_LATENCY_BUCKET,
                                               (start, end), consumers):
                    continue
                if kind == PROMQL_HEAD_TRANSPARENT:
                    continue
                if kind == PROMQL_HEAD_SELECTING:
                    bad.append(f"{label}{where[1:]}: `{head}(…)` SELECTS series out of the bucket "
                               "ladder — it keeps `le` (that part of the old message was wrong), "
                               "but a ladder IS its boundaries, so the ones it does not pick are "
                               "gone and the quantile interpolates over a ladder with holes "
                               "(measured: p20 0.3 against a true 0.06, and a NaN sample when "
                               "`+Inf` is the boundary dropped — calibration C7/C8'/C9')")
                    continue
                if kind is None:
                    bad.append(f"{label}{where[1:]}: `{head}(…)` is applied to "
                               f"{TRAEFIK_SERVICE_LATENCY_BUCKET} and this check does not know "
                               "whether it keeps the `le` label — classify it in "
                               "PROMQL_AGGREGATION_OPERATORS or PROMQL_LABEL_TRANSPARENT_CALLS")
                    continue
                names = _promql_label_set(labels)
                if clause is None:
                    bad.append(f"{label}{where[1:]}: `{head}(…)` aggregates the bucket series with "
                               "NO `by (…)`/`without (…)` modifier, so every label including `le` "
                               "is collapsed and the quantile has no boundaries left to "
                               "interpolate (measured: calibration rows B2/B4)")
                elif clause == "by" and "le" not in names:
                    bad.append(f"{label}{where[1:]}: `{head} by ({labels})` drops the `le` label, "
                               "so the quantile is computed over a series with no boundaries — "
                               "Grafana draws it anyway")
                elif clause == "without" and "le" in names:
                    bad.append(f"{label}{where[1:]}: `{head} without ({labels})` drops the `le` "
                               "label (same defect, other spelling)")
    if not reads:
        bad.append(f"no delivered dashboard reads {TRAEFIK_SERVICE_LATENCY_BUCKET} — Step 1a's "
                   "13-boundary ladder is tuned and nothing interpolates it")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: {reads} expression(s) across {len(docs)} delivered "
          f"dashboard(s) read {TRAEFIK_SERVICE_LATENCY_BUCKET} through histogram_quantile with "
          f"`le` kept (problems={bad})")
    return ok


def test_plex_library_panels_do_not_double_count_episodes() -> bool:
    """An aggregation over `plex_media_count` must not silently add the
    exporter's SYNTHETIC episode rows to its library titles.

    THE SAME CLASS AS THE SELECTOR ROW ABOVE — a panel that is never empty and is
    always wrong — and it arrived the same way, as a review finding on this very
    dashboard. `collect_media_metrics` emits one series per library section,
    `{title=<library>, type=<library type>}`, and then, for a `show` library
    ONLY, a second series `{title="<library> - Episodes", type="show_episode"}`
    carrying that library's EPISODE count. So `sum(plex_media_count)` adds every
    TV library's episodes to its titles: it populates, it reads plausible, and it
    is wrong by the size of the TV library. Read off the pinned image, not off
    the exporter's README — see `PLEX_MEDIA_COUNT` for the source lines.

    NOTHING ELSE HERE CAN SEE IT. The vocabulary row next door prices NAMES and
    every name in `sum(plex_media_count)` is real; the datasource, delivery, uid
    and mode rows never look at an expression's meaning; and 4d's operator, who
    is asked to confirm the panels populate, would tick it. That is the whole
    argument for spending a check on it.

    THE RULE IS "THE ROWS ENTERING THIS CALL CANNOT BE OF BOTH KINDS", NOT "THIS
    ONE MATCHER IS WRITTEN". Rounds 2-4 wrote the selector half as the literal
    `type!="show_episode"` and round 5 was rejected for it: an EQUALITY on a
    distinguishing label admits ONE value, so there is no synthetic row and a real
    row in the same call to add together, and four correct panels were RED —
    `sum(plex_media_count{type="show_episode"})`, the EPISODE TOTAL the exporter
    synthesises that row FOR (engine 50), `{type="movie"}` (7), `{title="TV"}` (3)
    and `{type=~"movie|show"}` (10). Each was refused with a sentence claiming its
    episodes were added to its titles, which none of them could do — the same
    "factually false refusal" complaint round 4 upheld against the `topk` message
    and fixed in that very commit, living in the other half of the same check.

    WHAT COUNTS AS CORRECT, and every shape that achieves the EFFECT is accepted
    rather than one being mandated, because which reading a dashboard wants is an
    authoring choice and a guard that picked one would be forbidding the rest:
      * PIN THE KIND IN THE SELECTOR, in EVERY selector the aggregation reaches —
        which is a per-CALL question and was asked per-EXPRESSION until round 4.
        `sum(plex_media_count{type!="show_episode"}) / sum(plex_media_count)` was
        GREEN because its numerator was right; the engine returns 10/60 for it
        (calibration D2). Excluding the synthetic type is one spelling of the pin,
        an equality is another, and a regex is decided by asking it — see
        `_plex_media_matcher_pins_one_kind` for all four operators, measured, and
        `_plex_media_mixed_selector` for the per-call quantifier, and the
        paragraph below for what happens when the selector cannot be read at all;
      * KEEP A LABEL THAT TELLS THEM APART through the aggregation. The synthetic
        row differs from a real one in BOTH of the family's labels, so `by (type)`,
        `by (title)`, `without (type)` and `without (title)` all leave it a series
        of its own — measured, all four shapes, in the real engine (B8/B9/B10).
        Round 2 wrote this rule over `type` ALONE and therefore refused
        `sum by (title) (…)`, which does not double-count at all: the rule was
        per-LABEL while its own justification is per-EFFECT, which is the
        DEC-075/077 failure in the row's own accept side. `PLEX_MEDIA_DISTINGUISHING_LABELS`
        is the fix, and only a grouping that keeps NEITHER label is the defect;
      * do not aggregate at all, in which case every library is its own series.

    AND WHEN THE SELECTOR CANNOT BE READ, THIS REFUSES WITHOUT CLAIMING THE
    DOUBLE COUNT. `_plex_media_mixed_selector` answers whether the mix was
    DEMONSTRATED or merely not ruled out, and the sentence printed below turns on
    that flag. The unreadable cases are a matcher list the Prometheus parser also
    refuses and a regex outside the syntax this gate's `re` and the engine's RE2
    share; for those, "the panel populates and is wrong by the size of the TV
    library" is a fact about the rows that nobody here established, and round 6
    printed it over all of them while the helper underneath was being careful not
    to. A three-valued predicate only stops a false refusal if the OUTERMOST
    sentence a reader meets stops asserting it too.

    A TOP-N PANEL IS NOT A DOUBLE COUNT. `topk`/`bottomk` select whole series and
    leave every label on them — `topk(3, plex_media_count)` returns three
    labelled series and merges nothing (calibration C1/C2/C3) — so the synthetic
    row stays a row of its own and this check has nothing to say about it. The
    refusal it used to print, "every `show` library's EPISODE count is added to
    its title count", was factually false there. What is NOT free is a merge
    stacked under the selection: `topk(3, sum(plex_media_count))` still reddens on
    the `sum` (battery R16).

    THE SIBLING ROW REFUSES THE SAME HEAD, deliberately, and the two are not in
    disagreement: they read the same classification and price it where their own
    harm is. Dropping a series here hides a library, which is exactly what a
    top-N panel asks for; dropping one THERE removes a boundary from a ladder and
    the quantile still draws (calibration C7/C9'). What the round-3 rework
    forbade was answering one QUESTION twice in two branches, and that is
    unchanged — `_promql_head_kind` is still the only place a head is classified.

    AN UNCLASSIFIED CALL HEAD IS RED HERE TOO, and that is the whole reason both
    rows now share `_promql_head_kind`. Round 2 shipped these two checks in one
    commit, for one class of defect, and they disagreed: the histogram row made
    an unknown head RED — with a paragraph arguing that a fail-CLOSED unknown is
    what keeps an incomplete list cheap — while this one wrote `continue` over
    it. Whichever way the argument goes it cannot go both ways in the same
    commit, and fail-closed is the direction the sibling already paid for.

    THE BOUND: this asks what an aggregation DOES with the labels that
    distinguish the synthetic rows, not whether the resulting number is the one
    the panel title promises — `by (title)` is accepted even though a library
    literally NAMED "X - Episodes" alongside a show library "X" would still
    merge, which is a Plex-side name collision no offline check can see, and which
    is also the one case where `{title="X"}` admits both kinds. A
    dashboard with no library panel at all satisfies this vacuously, and that is
    deliberate: the composite is not required to carry one, and the anti-vacuity
    that matters (a dashboard naming no `plex_*` series at all) is already
    charged next door.
    """
    body = _read(TASKS)
    if body is None:
        print("FAIL: plex library panels exclude episodes (tasks/main.yml unreadable)")
        return False
    if not _delivered_dashboards(body):
        print("FAIL: plex library panels exclude episodes (no dashboard is delivered)")
        return False
    docs, bad = _delivered_dashboard_documents(body)
    aggregations = 0
    subject = re.compile(rf"\b{PLEX_MEDIA_COUNT}\b")
    for label, doc in docs:
        for where, text in _promql_strings(doc):
            if not subject.search(text):
                continue
            for head, clause, labels, start, end in _promql_calls(text):
                if not subject.search(text, start, end):
                    continue
                kind = _promql_head_kind(head)
                if kind in (PROMQL_HEAD_TRANSPARENT, PROMQL_HEAD_QUANTILE,
                            PROMQL_HEAD_SELECTING):
                    continue
                if kind is None:
                    bad.append(f"{label}{where[1:]}: `{head}(…)` is applied to {PLEX_MEDIA_COUNT} "
                               "and this check does not know whether it MERGES the exporter's "
                               "synthetic episode rows into the real ones — classify it in "
                               "PROMQL_AGGREGATION_OPERATORS or PROMQL_LABEL_TRANSPARENT_CALLS")
                    continue
                aggregations += 1
                names = _promql_label_set(labels)
                if clause == "by":
                    kept = names & PLEX_MEDIA_DISTINGUISHING_LABELS
                elif clause == "without":
                    kept = PLEX_MEDIA_DISTINGUISHING_LABELS - names
                else:
                    kept = set()
                # THE SELECTOR QUESTION IS THIS CALL'S OWN, asked over the span it
                # is applied to — see `_plex_media_mixed_selector` for the fraction
                # panel that a per-expression flag let through.
                mixed = _plex_media_mixed_selector(text, (start, end))
                if mixed is None or kept:
                    continue
                demonstrated, why = mixed
                # THE OUTER SENTENCE ASSERTS ONLY WHAT WAS ESTABLISHED. An honest
                # inner clause inside a wrapper that flatly claims the double
                # count is the same factually false refusal one frame out — see
                # `_plex_media_mixed_selector` for the flag and why it exists.
                harm = ("so every `show` library's EPISODE count is added to its title count "
                        "and the panel populates and is wrong by the size of the TV library"
                        if demonstrated else
                        "and this check cannot establish that the rows entering it are all of "
                        "one kind, so it refuses rather than claims")
                bad.append(f"{label}{where[1:]}: `{head}(…)` "
                           f"{'aggregates rows of BOTH kinds' if demonstrated else 'aggregates'} "
                           f"and keeps none of {sorted(PLEX_MEDIA_DISTINGUISHING_LABELS)} through "
                           f"the aggregation, {harm} — {why}. Any of these is enough: exclude the "
                           f"synthetic rows (`{PLEX_MEDIA_EXCLUDED}`), pin the kind with an "
                           f"equality (`{PLEX_MEDIA_TYPE_LABEL}=\"{PLEX_MEDIA_SYNTHETIC_TYPE}\"` "
                           "for an episode total), or keep a distinguishing label through the "
                           "aggregation")
    ok = not bad
    print(f"{'OK' if ok else 'FAIL'}: {aggregations} aggregation(s) over {PLEX_MEDIA_COUNT} across "
          f"{len(docs)} delivered dashboard(s) either exclude or break out the exporter's "
          f"synthetic `{PLEX_MEDIA_SYNTHETIC_TYPE}` rows (problems={bad})")
    return ok


def test_dashboards_are_delivered_where_grafana_looks() -> bool:
    """provider path == the compose mount target == the delivery dest dir, AND
    the delivered file is NAMED something Grafana reads.

    Three files have to agree for a dashboard to be seen at all, and each of
    them can be edited alone: the provider's `options.path` is what Grafana
    scans, the compose `volumes:` entry is what puts host files there, and the
    delivery `dest` is what writes them. Reading all three is what keeps those
    three paths equal, which is the invariant the rest of this file's dest-keyed
    readers stand on.

    WHAT THIS CHECK DOES NOT DO — it used to say it did, and the sentence was
    wrong. `_delivered_dashboards` is keyed on the dest, so it only ever collects
    deliveries ALREADY INSIDE the dashboards tree: move the real pve delivery ONE
    DIRECTORY OVER and this clause prints OK (measured,
    `logs/rework-step04b-r4-inventory-content-post.log` W1). That shape is caught
    one function up, by `test_dashboard_delivery_inventory_is_complete` — the file
    it copies is delivered nowhere this reader can see, so it is an ORPHAN — and
    that is a check keyed on the dashboard's CONTENT, not on its filename, which
    is what makes it a real answer rather than a second convention. What this
    clause does see is a delivery one directory DOWN (W2). Attributed here so the
    next reader looking for "who catches a misdelivery" is sent to the check that
    actually does.

    THE NAME IS THE FOURTH THING, AND IT LIVES HERE BECAUSE "delivered where
    grafana LOOKS" is half a sentence without it. `_delivered_dashboards` now
    COMPUTES a delivered filename — a `dest:` naming the dashboards directory is
    keyed on the basename ansible gives it — and the model was confirmed against
    real ansible-core 2.21.1 (`logs/review-step04b-r2-dir-dest-ansible.log`,
    5/5): `template:` of a `foo.json.j2` src onto the bare directory writes a
    file STILL NAMED `foo.json.j2`. Ansible strips nothing. Nothing else in this
    file reads that name — the clause above takes `d.rsplit("/", 1)[0]` and
    compares only the DIRECTORY.

    Measured on real grafana/grafana:13.1.0 at the delivered root:root 0750/0640
    provisioning, fresh server per row (`logs/review-step04b-r2-suffix.log` 7/7):
    a dashboard delivered as `third.json.j2` is NOT LOADED, the server says
    NOTHING about it, the IDENTICAL BYTES named `third.json` ARE loaded, and a
    uid collision through a `.json.j2` name raises no duplicate warning at all
    because the file is never read. So `just play` succeeds, the mode is right,
    this guard printed PASS 13/13 — and the dashboard is absent on a healthy
    server. Silent, which is this loop's severity bar, not its completeness bar.

    BOTH DIRECTIONS OF THE RULE ARE MEASURED, not just the rejecting one:
      * what it REFUSES, the server would not have read anyway — Grafana matches
        `*.json` CASE-SENSITIVELY, so `.JSON`, `.yaml` and `.json.j2` are all
        silently ignored (`logs/review-step04b-r2-suffix-price.log` PART 1).
      * what it ACCEPTS, the server does read — including the odd name a suffix
        rule waves through: a DOT-FILE `.probe.json` is loaded, hidden or not
        (`logs/rework-step04b-r3-accepted-names-live.log` C2). The rule is the
        suffix and only the suffix.

    The price is on the DELIVERED name, never on how the role spells the source:
    a genuinely templated dashboard rendered to a `.json` dest stays GREEN
    (`logs/rework-step04b-r3-name-spellings-post.log` N6).

    ONE KNOWN, MEASURED STRICTNESS in the directory clause above: the provider
    RECURSES, so `dashboards/sub/foo.json` is loaded by the real server (C3 of
    the same log) while this check reddens on it. That RED is deliberate and it
    is LOUD — `just test` exits 1 and nobody ships blind. Keeping the three
    paths equal is the invariant that makes the other three agreements checkable;
    a subdirectory would also flatten into General under
    `foldersFromFilesStructure: false`. Recorded so the next reader finds a
    priced decision rather than an assumption (DEC-074).
    """
    provider, compose_body, tasks_body = _read(DASHBOARDS_TPL), _read(COMPOSE), _read(TASKS)
    if provider is None or compose_body is None or tasks_body is None:
        print("FAIL: dashboards delivered where grafana looks (a source file is unreadable)")
        return False
    m = re.search(r"(?m)^\s+options:\s*$", provider)
    scanned = _scalar(provider[m.end():], "path") if m else None
    block = _compose_service_block(compose_body, GRAFANA_SERVICE)
    mounted_from = _mount_source(block, scanned) if scanned else None
    delivered = [d for _n, _s, d, _r in _delivered_dashboards(tasks_body)]
    dests = {d.rsplit("/", 1)[0] for d in delivered}
    misnamed = sorted(d for d in delivered if not d.endswith(".json"))
    ok = (scanned == DASHBOARDS_MOUNT and mounted_from == DASHBOARDS_DIR
          and dests == {DASHBOARDS_DIR} and not misnamed)
    print(f"{'OK' if ok else 'FAIL'}: provider scans {scanned!r}, compose mounts it from "
          f"{mounted_from!r}, deliveries write to {sorted(dests)!r} "
          f"(not named *.json: {misnamed})")
    return ok


def main() -> int:
    # THE VERDICT MUST REACH THE READER EVEN WHEN THE CONSOLE CANNOT SPELL IT.
    # `_read` now names a bad byte in a sentence, and this file's sentences are
    # full of `—`; under `LC_ALL=en_US.iso88591` stdout is latin-1, so PRINTING
    # that sentence raised `UnicodeEncodeError` and cost the summary line the very
    # way the decode used to (`logs/red-579d-read-invalid-utf8.py` PART C, 4/4
    # `verdict=None` before this). Only the ERROR POLICY is set: the encoding is
    # still the console's, so nothing about a UTF-8 terminal's output changes, and
    # a console that cannot spell an em dash gets a `?` instead of a traceback.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    results = [
        test_guarded_files_exist(),
        test_grafana_service_keeps_the_root_group(),
        test_grafana_provisioning_dirs_are_traversable(),
        test_grafana_delivered_files_are_readable(),
        test_datasource_declares_an_explicit_uid(),
        test_datasource_uid_change_is_migrated(),
        test_provisioning_files_have_no_duplicate_key(),
        test_delivered_dashboards_reference_the_provisioned_uid(),
        test_delivered_dashboard_datasource_types_agree_with_the_provisioned_uid(),
        test_dashboard_delivery_inventory_is_complete(),
        test_delivered_dashboards_parse_as_dashboards(),
        test_delivered_dashboards_have_distinct_uids(),
        test_delivered_dashboards_have_distinct_titles(),
        test_pve_panels_name_series_the_exporter_declares(),
        test_plex_panels_name_series_the_exporter_declares(),
        test_delivered_dashboard_queries_are_readable(),
        test_dashboard_variables_are_declared_where_they_are_used(),
        test_pve_dashboard_declares_the_container_drop_down(),
        test_plex_latency_panels_select_the_file_provider_service(),
        test_plex_latency_panels_read_the_tuned_histogram_buckets(),
        test_plex_library_panels_do_not_double_count_episodes(),
        test_dashboards_are_delivered_where_grafana_looks(),
    ]
    total, passed = len(results), sum(results)
    if passed == total:
        print(f"PASS: {passed}/{total}")
        return 0
    print(f"FAIL: {total - passed}/{total} checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
