*! version 0.1.0  23oct2026  Energy Research Warehouse (ERW)
*! erw: the ERW in Stata, the six calls of docs/methods/packages.md (github.com/SamuelEnrique/erw)
*! erw tables | erw coverage | erw fetch | erw cite | erw license | erw standard
*! The live set and Redivis are read with curl (Windows 10 and later, macOS and Linux carry it), since Stata's own
*! copy cannot send the headers they ask for. Globals: ERW_LIVE_URL, ERW_LIVE_KEY, REDIVIS_API_TOKEN, ERW_DATA_DIR,
*! ERW_REPO (a clone, for the record files; else they are read from GitHub).
program define erw, rclass
    version 16

    gettoken sub 0 : 0, parse(" ,")

    if "`sub'" == "tables" {
        _erw_tables `0'
    }
    else if "`sub'" == "coverage" {
        _erw_coverage `0'
    }
    else if "`sub'" == "fetch" {
        _erw_fetch `0'
    }
    else if "`sub'" == "cite" {
        _erw_cite `0'
    }
    else if "`sub'" == "license" {
        _erw_license `0'
    }
    else if "`sub'" == "standard" {
        _erw_standard `0'
    }
    else {
        display as error "erw: the calls are erw tables, erw coverage, erw fetch, erw cite, erw license and erw standard"
        exit 198
    }

    return add
end

program define _erw_record
    syntax anything(name=which), SAVing(string)

    if "`which'" == "coverage" {
        local rel "warehouse/metadata/coverage.csv"
    }
    else if "`which'" == "sources" {
        local rel "warehouse/metadata/sources.csv"
    }
    else if "`which'" == "licenses" {
        local rel "package/src/erw/data/tables.csv"
    }
    else {
        local rel "warehouse/metadata/table_migrations.csv"
    }

    if `"$ERW_REPO"' != "" {
        quietly copy `"$ERW_REPO/`rel'"' `"`saving'"', replace
    }
    else {
        quietly copy `"https://raw.githubusercontent.com/SamuelEnrique/erw/main/`rel'"' `"`saving'"', replace
    }
end

program define _erw_import
    syntax using/

    tempname fh

    file open `fh' using `"`using'"', read text

    file read `fh' line

    local n 0

    while r(eof) == 0 & substr(`"`macval(line)'"', 1, 1) == "#" {
        local n = `n' + 1
        file read `fh' line
    }

    file close `fh'

    import delimited using `"`using'"', clear varnames(`=`n' + 1') rowrange(`=`n' + 2') stringcols(_all) encoding("utf-8") bindquote(strict) maxquotedrows(unlimited)
end

program define _erw_row, rclass
    syntax anything(name=value), FILE(string) KEY(string) FIELDS(string)

    preserve

    quietly _erw_import using `"`file'"'

    quietly keep if `key' == `"`value'"'

    return scalar found = _N

    foreach f of local fields {
        if _N > 0 {
            return local `f' = `f'[1]
        }
    }

    restore
end

program define _erw_shape, rclass
    syntax anything(name=table), FILE(string)

    _erw_row `table', file(`"`file'"') key(table) fields(interval)

    if r(found) == 0 {
        display as error "No ERW table named `table'. erw tables lists every table."
        exit 111
    }

    local interval "`r(interval)'"

    return local shape = cond("`interval'" == "snapshot", "entities", cond("`interval'" == "event", "events", "series"))
end

program define _erw_live_url, rclass
    syntax anything(name=table), BASE(string) SHAPE(string) [ENTity(string) VARiable(string) Start(string) End(string) OFFset(integer 0) LIMit(integer 1000)]

    if "`shape'" == "series" {
        local tcol "ts_utc"
        local vcol "variable"
        local order "entity,variable,ts_utc,event"
    }
    else if "`shape'" == "entities" {
        local tcol "status_date"
        local vcol "entity_type"
        local order "entity_id"
    }
    else {
        local tcol "event_date"
        local vcol "event_type"
        local order "event_id"
    }

    local q "select=*&table_name=eq.`table'"

    if "`entity'" != "" {
        local list ""
        local sep ""
        local colon 0
        local plain 0
        foreach e of local entity {
            local v "`e'"
            local v : subinstr local v "%" "%25", all
            local v : subinstr local v "+" "%2B", all
            local v : subinstr local v "/" "%2F", all
            local v : subinstr local v "&" "%26", all
            local list "`list'`sep'%22`v'%22"
            local sep ","
            if strpos("`e'", ":") > 0 {
                local colon 1
            }
            else {
                local plain 1
            }
        }
        if "`shape'" == "entities" {
            local q "`q'&entity_id=in.(`list')"
        }
        else if "`shape'" == "events" {
            local q "`q'&source=in.(`list')"
        }
        else if "`plain'" == "0" {
            local q "`q'&entity=in.(`list')"
        }
        else if "`colon'" == "0" {
            local q "`q'&node=in.(`list')"
        }
    }

    if "`variable'" != "" {
        local list ""
        local sep ""
        foreach v of local variable {
            local list "`list'`sep'%22`v'%22"
            local sep ","
        }
        local q "`q'&`vcol'=in.(`list')"
    }

    if "`start'" != "" {
        local t "`start'"
        if strlen("`t'") == 10 {
            local t "`t'T00:00:00Z"
        }
        local q "`q'&`tcol'=gte.`t'"
    }

    if "`end'" != "" {
        local t "`end'"
        if strlen("`t'") == 10 {
            local t "`t'T00:00:00Z"
        }
        local q "`q'&`tcol'=lt.`t'"
    }

    local q "`q'&order=`order'&limit=`limit'&offset=`offset'"

    return local url "`base'/rest/v1/`shape'?`q'"
end

program define _erw_live_read
    syntax anything(name=table), SHAPE(string) [ENTity(string) VARiable(string) Start(string) End(string) LIMit(integer 0)]

    if `"$ERW_LIVE_URL"' == "" | `"$ERW_LIVE_KEY"' == "" {
        display as error "Set ERW_LIVE_URL and ERW_LIVE_KEY to the live set's address and key (the ERW gives them on request), then try again."
        exit 198
    }

    local base `"$ERW_LIVE_URL"'

    local base : subinstr local base "/rest/v1/" "", all

    local base : subinstr local base "/rest/v1" "", all

    if substr(`"`base'"', -1, 1) == "/" {
        local base = substr(`"`base'"', 1, strlen(`"`base'"') - 1)
    }

    local page_rows = cond(`limit' > 0, `limit', 1000)

    tempfile all page

    local offset 0

    local more 1

    local first 1

    while `more' {
        _erw_live_url `table', base(`"`base'"') shape(`shape') entity(`entity') variable(`variable') start(`start') end(`end') offset(`offset') limit(`page_rows')
        local url `"`r(url)'"'
        capture erase `"`page'"'
        shell curl -sS -f -H "apikey: $ERW_LIVE_KEY" -H "Authorization: Bearer $ERW_LIVE_KEY" -H "Accept: text/csv" -o "`page'" "`url'"
        capture confirm file `"`page'"'
        if _rc {
            display as error "The ERW's live set could not be reached (curl wrote no file). Check the network connection, then try again."
            exit 631
        }
        capture quietly _erw_import using `"`page'"'
        if _rc {
            quietly drop _all
        }
        local got = _N
        if `got' > `page_rows' {
            display as error "The live set answered a page of `got' rows where `page_rows' were asked for: a fault of the package, not of your call; please tell the ERW (https://github.com/SamuelEnrique/erw/issues)."
            exit 459
        }
        tempfile p
        quietly save `"`p'"', emptyok
        if `first' {
            quietly save `"`all'"', replace emptyok
        }
        else {
            quietly use `"`all'"', clear
            quietly append using `"`p'"'
            quietly save `"`all'"', replace emptyok
        }
        local first 0
        local offset = `offset' + `page_rows'
        local more = (`got' == `page_rows') & (`limit' == 0)
    }

    quietly use `"`all'"', clear

    foreach v in table_name license loaded_at {
        capture drop `v'
    }
end

program define _erw_redivis_read
    syntax anything(name=table) [, LIMit(integer 0)]

    if `"$REDIVIS_API_TOKEN"' == "" {
        display as error "Set REDIVIS_API_TOKEN to a token from https://redivis.com/workspace/settings/tokens, then try again."
        exit 198
    }

    local url "https://redivis.com/api/v1/tables/datapages.erw:b9wm.`table'/rows?format=csv"

    if `limit' > 0 {
        local url "`url'&maxResults=`limit'"
    }

    tempfile page

    shell curl -sS -f -H "Authorization: Bearer $REDIVIS_API_TOKEN" -o "`page'" "`url'"

    capture confirm file `"`page'"'

    if _rc {
        display as error "The ERW's Redivis could not be reached (curl wrote no file). Check the network connection, then try again."
        exit 631
    }

    quietly _erw_import using `"`page'"'
end

program define _erw_time
    syntax varname

    tempvar t

    quietly gen double `t' = clock(substr(subinstr(`varlist', "T", " ", 1), 1, 19), "YMDhms")

    quietly replace `t' = clock(substr(`varlist', 1, 10) + " 00:00:00", "YMDhms") if missing(`t') & strlen(`varlist') == 10

    format `t' %tc

    order `t', before(`varlist')

    drop `varlist'

    rename `t' `varlist'
end

program define _erw_date
    syntax varname

    tempvar t

    quietly gen long `t' = date(substr(`varlist', 1, 10), "YMD")

    format `t' %td

    order `t', before(`varlist')

    drop `varlist'

    rename `t' `varlist'
end

program define _erw_types
    syntax , SHAPE(string)

    if "`shape'" == "series" {
        quietly destring value, replace force
        _erw_time ts_utc
    }
    else if "`shape'" == "entities" {
        foreach v of varlist _all {
            if inlist("`v'", "lat", "lon", "capacity_mw") | substr("`v'", -3, 3) == "_mw" {
                quietly destring `v', replace force
            }
            if "`v'" == "status_date" | substr("`v'", -5, 5) == "_date" {
                _erw_date `v'
            }
            if "`v'" == "retrieved_at" {
                _erw_time `v'
            }
        }
    }
    else {
        _erw_time event_date
        foreach v in mw price significance ai_power_relevance {
            capture quietly destring `v', replace force
        }
    }
end

program define _erw_filter
    syntax , SHAPE(string) [ENTity(string) VARiable(string) Start(string) End(string)]

    if "`shape'" == "series" {
        local ecol "entity"
        local vcol "variable"
        local tcol "ts_utc"
    }
    else if "`shape'" == "entities" {
        local ecol "entity_id"
        local vcol "entity_type"
        local tcol "status_date"
    }
    else {
        local ecol "source"
        local vcol "event_type"
        local tcol "event_date"
    }

    if "`entity'" != "" {
        tempvar k
        quietly gen byte `k' = 0
        foreach e of local entity {
            quietly replace `k' = 1 if `ecol' == "`e'"
            capture quietly replace `k' = 1 if node == "`e'"
            capture quietly replace `k' = 1 if name == "`e'" & "`shape'" == "entities"
        }
        quietly keep if `k'
        drop `k'
    }

    if "`variable'" != "" {
        tempvar k
        quietly gen byte `k' = 0
        foreach v of local variable {
            quietly replace `k' = 1 if `vcol' == "`v'"
        }
        quietly keep if `k'
        drop `k'
    }

    foreach side in start end {
        if "``side''" != "" {
            tempname s
            scalar `s' = clock(substr(subinstr("``side''", "T", " ", 1), 1, 19), "YMDhms")
            if missing(`s') {
                scalar `s' = clock(substr("``side''", 1, 10) + " 00:00:00", "YMDhms")
            }
            if "`shape'" == "entities" & "`side'" == "start" {
                quietly keep if `tcol' >= dofc(`s') & !missing(`tcol')
            }
            else if "`shape'" == "entities" {
                quietly keep if `tcol' < dofc(`s') & !missing(`tcol')
            }
            else if "`side'" == "start" {
                quietly keep if `tcol' >= `s'
            }
            else {
                quietly keep if `tcol' < `s'
            }
        }
    }
end

program define _erw_route, rclass
    syntax anything(name=table) [, WINdow(string) Start(string)]

    if `"$ERW_DATA_DIR"' != "" {
        capture confirm file `"$ERW_DATA_DIR/`table'.csv"'
        if _rc == 0 {
            return local backend "local"
            exit
        }
    }

    local live 0

    if `"$ERW_LIVE_URL"' != "" & `"$ERW_LIVE_KEY"' != "" {
        if inlist("`window'", "whole", "some rows") {
            local live 1
        }
        else if word("`window'", 2) == "days" & "`start'" != "" {
            local live = date(substr("`start'", 1, 10), "YMD") >= date(c(current_date), "DMY") - (real(word("`window'", 1)) - 5)
        }
    }

    if `live' {
        return local backend "live"
    }
    else {
        return local backend "redivis"
    }
end

program define _erw_fetch, rclass
    syntax anything(name=table) [, ENTity(string) VARiable(string) Start(string) End(string) BACKend(string) CLEAR]

    local table `table'

    if c(changed) & "`clear'" == "" {
        display as error "no; dataset in memory has changed since last saved (erw fetch ..., clear)"
        exit 4
    }

    if "`backend'" == "" {
        local backend "auto"
    }

    tempfile lic cov

    _erw_record licenses, saving(`"`lic'"')

    _erw_record coverage, saving(`"`cov'"')

    _erw_shape `table', file(`"`cov'"')

    local shape "`r(shape)'"

    _erw_row `table', file(`"`lic'"') key(table) fields(verdict words live_window)

    local verdict "`r(verdict)'"

    local words `"`r(words)'"'

    local window "`r(live_window)'"

    if "`backend'" == "auto" {
        _erw_route `table', window(`window') start(`start')
        local backend "`r(backend)'"
    }

    if !inlist("`backend'", "local", "live", "redivis") {
        display as error "erw: backend() is auto, local, live or redivis"
        exit 198
    }

    if "`verdict'" != "" & "`verdict'" != "public" & "`backend'" != "local" {
        display as error `"`table' is not public: `verdict'. `macval(words)' The ERW's license record: https://github.com/SamuelEnrique/erw/blob/main/docs/licenses.md"'
        exit 498
    }

    if "`verdict'" != "" & "`verdict'" != "public" {
        display as text `"(`table' is not public (`verdict'): `macval(words)' Read from local files, your own copy under its own license.)"'
    }

    if "`backend'" == "local" {
        _erw_import using `"$ERW_DATA_DIR/`table'.csv"'
    }
    else if "`backend'" == "live" {
        _erw_live_read `table', shape(`shape') entity(`entity') variable(`variable') start(`start') end(`end')
    }
    else {
        _erw_redivis_read `table'
    }

    _erw_types, shape(`shape')

    _erw_filter, shape(`shape') entity(`entity') variable(`variable') start(`start') end(`end')

    if _N == 0 & ("`start'" != "" | "`end'" != "") {
        _erw_row `table', file(`"`cov'"') key(table) fields(ts_min ts_max)
        local s = cond("`start'" == "", "the first row", "`start'")
        local e = cond("`end'" == "", "the last row", "`end'")
        display as text "No rows of `table' start in [`s', `e'); its rows run from `r(ts_min)' to `r(ts_max)'."
    }

    local where = cond("`backend'" == "local", "local files", cond("`backend'" == "live", "the live set", "Redivis datapages.erw:b9wm latest release"))

    local stamp "`c(current_date)' `c(current_time)'"

    local line "ERW `table': `where'; ERW commit unknown; fetched `stamp' (this computer's clock); `=_N' rows"

    char _dta[erw_version] "`line'"

    char _dta[erw_license] "`verdict'"

    char _dta[erw_backend] "`backend'"

    char _dta[erw_fetched] "`stamp'"

    display as text "`line'"

    return local version "`line'"

    return local backend "`backend'"

    return scalar N = _N
end

program define _erw_tables
    syntax [, CLEAR]

    if c(changed) & "`clear'" == "" {
        display as error "no; dataset in memory has changed since last saved (erw tables, clear)"
        exit 4
    }

    tempfile lic cov l

    _erw_record licenses, saving(`"`lic'"')

    _erw_record coverage, saving(`"`cov'"')

    quietly _erw_import using `"`lic'"'

    quietly keep table verdict live_window

    quietly save `"`l'"'

    quietly _erw_import using `"`cov'"'

    quietly merge 1:1 table using `"`l'"', keep(master match) nogenerate

    quietly gen shape = cond(interval == "snapshot", "entities", cond(interval == "event", "events", "series"))

    quietly gen in_live = cond(inlist(live_window, "", "none"), "no", "yes")

    quietly destring n_rows, replace force

    keep table shape interval ts_min ts_max n_rows verdict in_live

    order table shape interval ts_min ts_max n_rows verdict in_live

    display as text "`=_N' ERW tables (erw license <table> says why one is not public)"
end

program define _erw_coverage
    syntax [anything(name=table)] [, CLEAR]

    if c(changed) & "`clear'" == "" {
        display as error "no; dataset in memory has changed since last saved (erw coverage ..., clear)"
        exit 4
    }

    tempfile lic cov l

    _erw_record licenses, saving(`"`lic'"')

    _erw_record coverage, saving(`"`cov'"')

    quietly _erw_import using `"`lic'"'

    quietly keep table verdict live_window

    quietly save `"`l'"'

    quietly _erw_import using `"`cov'"'

    quietly merge 1:1 table using `"`l'"', keep(master match) nogenerate

    quietly destring n_nodes n_rows, replace force

    if `"`table'"' != "" {
        quietly keep if table == `"`table'"'
        if _N == 0 {
            display as error "No ERW table named `table'. erw tables lists every table."
            exit 111
        }
    }
end

program define _erw_license, rclass
    syntax anything(name=table)

    tempfile lic

    _erw_record licenses, saving(`"`lic'"')

    _erw_row `table', file(`"`lic'"') key(table) fields(verdict status status_from decided_by publishers words)

    if r(found) == 0 {
        display as error "No ERW table named `table'. erw tables lists every table."
        exit 111
    }

    display as text `"`table': `r(verdict)'. `macval(r(words))'"'

    return add
end

program define _erw_cite, rclass
    syntax anything(name=table)

    local table `table'

    local bt = char(96)

    tempfile src lic mig

    _erw_record sources, saving(`"`src'"')

    _erw_record licenses, saving(`"`lic'"')

    _erw_record migrations, saving(`"`mig'"')

    preserve

    quietly _erw_import using `"`mig'"'

    quietly keep if new_table == "`table'"

    local wanted "`table'"

    forvalues i = 1/`=_N' {
        local wanted "`wanted' `=old_table[`i']'"
    }

    quietly _erw_import using `"`src'"'

    quietly gen byte hit = 0

    quietly gen tl = ";" + subinstr(subinstr(tables, ",", ";", .), " ", "", .) + ";"

    foreach w of local wanted {
        quietly replace hit = 1 if strpos(tl, ";`w';") > 0
    }

    quietly keep if hit

    local head ""

    local reports ""

    quietly levelsof publisher if publisher != "", local(pubs)

    foreach p of local pubs {
        local head = cond(`"`macval(head)'"' == "", `"`macval(p)'"', `"`macval(head)'; `macval(p)'"')
    }

    quietly levelsof report if report != "", local(reps)

    foreach r of local reps {
        local reports = cond(`"`macval(reports)'"' == "", `"`macval(r)'"', `"`macval(reports)'; `macval(r)'"')
    }

    restore

    if `"`macval(head)'"' == "" {
        _erw_row `table', file(`"`lic'"') key(table) fields(publishers)
        local head `"`r(publishers)'"'
    }

    if `"`macval(head)'"' == "" {
        local head "Energy Research Warehouse (ERW)"
    }

    if `"`macval(reports)'"' != "" {
        local reports `" `macval(reports)'."'
    }

    local backend : char _dta[erw_backend]

    local fetched : char _dta[erw_fetched]

    if "`backend'" == "live" {
        local clause "the live set, fetched `fetched' (this computer's clock)"
    }
    else if "`backend'" == "local" {
        local clause "local files (no ERW commit identifies them)"
    }
    else {
        local clause "Redivis dataset `bt'datapages.erw`bt', version <the version you read>"
    }

    local cite `"`macval(head)'.`macval(reports)' Via the Energy Research Warehouse (ERW), table `bt'`table'`bt', `clause'."'

    display as text `"`macval(cite)'"'

    return local cite `"`macval(cite)'"'
end

program define _erw_standard, rclass
    syntax anything(name=table) [, BACKend(string) CLEAR]

    local table `table'

    if c(changed) & "`clear'" == "" {
        display as error "no; dataset in memory has changed since last saved (erw standard ..., clear)"
        exit 4
    }

    tempfile cov

    _erw_record coverage, saving(`"`cov'"')

    _erw_shape `table', file(`"`cov'"')

    local shape "`r(shape)'"

    if "`backend'" == "" {
        _erw_route `table', window(whole)
        local backend "`r(backend)'"
    }

    if "`backend'" == "local" {
        _erw_import using `"$ERW_DATA_DIR/`table'.csv"'
    }
    else if "`backend'" == "live" {
        _erw_live_read `table', shape(`shape') limit(1)
    }
    else {
        _erw_redivis_read `table', limit(1)
    }

    quietly ds

    local cols "`r(varlist)'"

    if "`shape'" == "series" {
        local req "entity variable ts_utc value"
        local res "unit freq geo market node source source_url retrieved_at vintage"
        local part "ba year event"
        local key "entity variable ts_utc"
    }
    else if "`shape'" == "entities" {
        local req "entity_id entity_type name source"
        local res "geo lat lon capacity_mw status status_date operator source_url retrieved_at vintage"
        local part ""
        local key "entity_id"
    }
    else {
        local req "event_id event_date event_type source source_url"
        local res "parties entity_ids mw price currency status"
        local part ""
        local key "event_id"
    }

    quietly drop _all

    local n : word count `cols'

    quietly set obs `n'

    quietly gen name = ""

    quietly gen type = "text"

    quietly gen required = "extra"

    forvalues i = 1/`n' {
        local c : word `i' of `cols'
        quietly replace name = "`c'" in `i'
        if "`shape'" == "series" & "`c'" == "value" {
            quietly replace type = "number" in `i'
        }
        if "`shape'" == "series" & "`c'" == "ts_utc" {
            quietly replace type = "utc time" in `i'
        }
        if "`shape'" == "entities" & (inlist("`c'", "lat", "lon", "capacity_mw") | substr("`c'", -3, 3) == "_mw") {
            quietly replace type = "number" in `i'
        }
        if "`shape'" == "entities" & ("`c'" == "status_date" | substr("`c'", -5, 5) == "_date") {
            quietly replace type = "date" in `i'
        }
        if "`shape'" == "entities" & "`c'" == "retrieved_at" {
            quietly replace type = "utc time" in `i'
        }
        if "`shape'" == "events" & "`c'" == "event_date" {
            quietly replace type = "utc time" in `i'
        }
        if "`shape'" == "events" & inlist("`c'", "mw", "price", "significance", "ai_power_relevance") {
            quietly replace type = "number" in `i'
        }
        if strpos(" `req' ", " `c' ") > 0 {
            quietly replace required = "yes" in `i'
        }
        else if strpos(" `res' ", " `c' ") > 0 {
            quietly replace required = "reserved" in `i'
        }
        else if strpos(" `part' ", " `c' ") > 0 {
            quietly replace required = "partition" in `i'
        }
    }

    display as text "`table': `shape', key `key'"

    return local shape "`shape'"

    return local key "`key'"
end
