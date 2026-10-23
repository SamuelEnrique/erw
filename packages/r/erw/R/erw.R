# erw: the Energy Research Warehouse (ERW) in R, the six calls of docs/methods/packages.md (session 1005, chain 070).
# Base R only: utils::download.file (method "libcurl", which sends headers) and utils::read.csv. The live set is read
# through its REST address with the anon key (ERW_LIVE_URL, ERW_LIVE_KEY), Redivis through the address its own client
# reads small tables with (REDIVIS_API_TOKEN), local files from ERW_DATA_DIR. The record files (coverage, the source
# registry, the license record, the table migrations) come from ERW_REPO, a clone, or else from GitHub.

.erw_raw <- "https://raw.githubusercontent.com/SamuelEnrique/erw/main"

.erw_paths <- c(coverage = "warehouse/metadata/coverage.csv",
                sources = "warehouse/metadata/sources.csv",
                licenses = "package/src/erw/data/tables.csv",
                migrations = "warehouse/metadata/table_migrations.csv",
                release = "docs/redivis/release-v1-stanford/tables.csv")   # session 1014: each table's title line

.erw_state <- new.env(parent = emptyenv())

.erw_read_csv <- function(path) {
  head <- readLines(path, n = 500L, encoding = "UTF-8", warn = FALSE)
  n <- 0L
  while (n < length(head) && startsWith(head[n + 1L], "#")) n <- n + 1L
  utils::read.csv(path, skip = n, colClasses = "character", na.strings = character(0), check.names = FALSE,
                  encoding = "UTF-8", stringsAsFactors = FALSE)
}

.erw_record <- function(which) {
  key <- paste0("record_", which)
  if (!is.null(.erw_state[[key]])) return(.erw_state[[key]])
  repo <- Sys.getenv("ERW_REPO")
  if (nzchar(repo)) {
    path <- file.path(repo, .erw_paths[[which]])
  } else {
    path <- tempfile(fileext = ".csv")
    utils::download.file(paste0(.erw_raw, "/", .erw_paths[[which]]), path, quiet = TRUE, mode = "wb")
  }
  out <- .erw_read_csv(path)
  .erw_state[[key]] <- out
  out
}

.erw_shape <- function(table) {
  cov <- .erw_record("coverage")
  row <- cov[cov$table == table, , drop = FALSE]
  if (nrow(row) == 0) stop(sprintf("No ERW table named %s. erw_tables() lists every table.", table), call. = FALSE)
  if (row$interval[1] == "snapshot") "entities" else if (row$interval[1] == "event") "events" else "series"
}

.erw_live_base <- function() {
  base <- Sys.getenv("ERW_LIVE_URL", Sys.getenv("SUPABASE_URL"))
  key <- Sys.getenv("ERW_LIVE_KEY", Sys.getenv("SUPABASE_ANON_KEY"))
  if (!nzchar(base) || !nzchar(key)) {
    stop("Set ERW_LIVE_URL and ERW_LIVE_KEY to the live set's address and key (the ERW gives them on request), then try again.",
         call. = FALSE)
  }
  base <- sub("/rest/v1/?$", "", base)
  base <- sub("/$", "", base)
  list(base = base, key = key)
}

.erw_live_url <- function(table, base, shape, entity = NULL, variable = NULL, start = NULL, end = NULL,
                          offset = 0L, limit = 1000L) {
  if (shape == "series") {
    tcol <- "ts_utc"
    vcol <- "variable"
    order <- "entity,variable,ts_utc,event"
  } else if (shape == "entities") {
    tcol <- "status_date"
    vcol <- "entity_type"
    order <- "entity_id"
  } else {
    tcol <- "event_date"
    vcol <- "event_type"
    order <- "event_id"
  }
  q <- paste0("select=*&table_name=eq.", table)
  if (length(entity) > 0) {
    items <- ""
    sep <- ""
    colon <- FALSE
    plain <- FALSE
    for (e in entity) {
      v <- gsub("%", "%25", e, fixed = TRUE)
      v <- gsub("+", "%2B", v, fixed = TRUE)
      v <- gsub("/", "%2F", v, fixed = TRUE)
      v <- gsub("&", "%26", v, fixed = TRUE)
      items <- paste0(items, sep, "%22", v, "%22")
      sep <- ","
      if (grepl(":", e, fixed = TRUE)) {
        colon <- TRUE
      } else {
        plain <- TRUE
      }
    }
    if (shape == "entities") {
      q <- paste0(q, "&entity_id=in.(", items, ")")
    } else if (shape == "events") {
      q <- paste0(q, "&source=in.(", items, ")")
    } else if (!plain) {
      q <- paste0(q, "&entity=in.(", items, ")")
    } else if (!colon) {
      q <- paste0(q, "&node=in.(", items, ")")
    }
  }
  if (length(variable) > 0) {
    items <- ""
    sep <- ""
    for (v in variable) {
      items <- paste0(items, sep, "%22", v, "%22")
      sep <- ","
    }
    q <- paste0(q, "&", vcol, "=in.(", items, ")")
  }
  if (length(start) > 0) {
    t <- start
    if (nchar(t) == 10) {
      t <- paste0(t, "T00:00:00Z")
    }
    q <- paste0(q, "&", tcol, "=gte.", t)
  }
  if (length(end) > 0) {
    t <- end
    if (nchar(t) == 10) {
      t <- paste0(t, "T00:00:00Z")
    }
    q <- paste0(q, "&", tcol, "=lt.", t)
  }
  q <- paste0(q, "&order=", order, "&limit=", as.integer(limit), "&offset=", as.integer(offset))
  paste0(base, "/rest/v1/", shape, "?", q)
}

.erw_count <- function(kind) {
  key <- paste0("requests_", kind)
  .erw_state[[key]] <- (if (is.null(.erw_state[[key]])) 0L else .erw_state[[key]]) + 1L
}

.erw_get <- function(url, headers, kind) {
  path <- tempfile(fileext = ".csv")
  .erw_count(kind)
  ok <- tryCatch({
    utils::download.file(url, path, quiet = TRUE, method = "libcurl", headers = headers, mode = "wb")
    TRUE
  }, error = function(e) FALSE, warning = function(w) FALSE)
  if (!ok || !file.exists(path)) {
    stop(sprintf("The ERW's %s could not be reached (the download wrote no file). Check the network connection, then try again.",
                 if (kind == "live") "live set" else "Redivis"), call. = FALSE)
  }
  path
}

.erw_live_read <- function(table, shape, entity = NULL, variable = NULL, start = NULL, end = NULL, limit = 0L) {
  live <- .erw_live_base()
  page <- if (limit > 0) limit else 1000L
  headers <- c(apikey = live$key, Authorization = paste("Bearer", live$key), Accept = "text/csv")
  parts <- list()
  offset <- 0L
  repeat {
    url <- .erw_live_url(table, live$base, shape, entity, variable, start, end, offset, page)
    path <- .erw_get(url, headers, "live")
    part <- if (file.info(path)$size > 0) .erw_read_csv(path) else data.frame()
    if (nrow(part) > page) {
      stop(sprintf("The live set answered a page of %d rows where %d were asked for: a fault of the package, not of your call; please tell the ERW (https://github.com/SamuelEnrique/erw/issues).",
                   nrow(part), as.integer(page)), call. = FALSE)
    }
    parts[[length(parts) + 1L]] <- part
    if (nrow(part) < page || limit > 0) break
    offset <- offset + page
  }
  out <- do.call(rbind, parts)
  out[, setdiff(names(out), c("table_name", "license", "loaded_at")), drop = FALSE]
}

.erw_redivis_read <- function(table, limit = 0L) {
  token <- Sys.getenv("REDIVIS_API_TOKEN")
  if (!nzchar(token)) {
    stop("Set REDIVIS_API_TOKEN to a token from https://redivis.com/workspace/settings/tokens, then try again.", call. = FALSE)
  }
  url <- paste0("https://redivis.com/api/v1/tables/datapages.erw:b9wm.", table, "/rows?format=csv")
  if (limit > 0) url <- paste0(url, "&maxResults=", as.integer(limit))
  got <- tryCatch(.erw_read_csv(.erw_get(url, c(Authorization = paste("Bearer", token)), "redivis")), error = function(e) NULL)
  if (!is.null(got)) return(got)
  # session 1014 (chain 070): Redivis refuses the rows of a stream once a user has streamed 100 GB in 30 days; the table
  # is then read through its export, as the Python package does (session 665): POST .../exports, wait for it to be
  # completed, then each file part. Base R cannot POST, so curl (Windows 10 and later, macOS and Linux) makes the calls.
  out <- .erw_redivis_export(table, token)
  if (limit > 0 && nrow(out) > limit) out <- out[seq_len(limit), , drop = FALSE]
  out
}

.erw_json_field <- function(path, field) {
  txt <- paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
  m <- regmatches(txt, regexpr(sprintf('"%s"\\s*:\\s*("[^"]*"|[0-9]+)', field), txt))
  if (!length(m)) return(NA_character_)
  gsub('"', "", sub(sprintf('"%s"\\s*:\\s*', field), "", m))
}

.erw_curl <- function(args, kind = "redivis") {
  .erw_count(kind)
  status <- suppressWarnings(system2("curl", args, stdout = FALSE, stderr = FALSE))
  if (!identical(as.integer(status), 0L)) {
    stop("The ERW's Redivis could not be reached (curl failed). Check the network connection, then try again.", call. = FALSE)
  }
}

.erw_redivis_export <- function(table, token) {
  api <- "https://redivis.com/api/v1"
  auth <- c("-H", shQuote(paste("Authorization: Bearer", token)))
  body <- tempfile(fileext = ".json")
  writeLines('{"format":"csv"}', body)
  made <- tempfile(fileext = ".json")
  .erw_curl(c("-sS", "-f", "-X", "POST", auth, "-H", shQuote("Content-Type: application/json"),
              "--data-binary", shQuote(paste0("@", body)), "-o", shQuote(made),
              shQuote(paste0(api, "/tables/datapages.erw:b9wm.", table, "/exports"))))
  id <- .erw_json_field(made, "id")
  if (is.na(id)) stop("Redivis did not start an export of ", table, ".", call. = FALSE)
  state <- tempfile(fileext = ".json")
  for (i in seq_len(240)) {
    .erw_curl(c("-sS", "-f", auth, "-o", shQuote(state), shQuote(paste0(api, "/exports/", id))))
    status <- .erw_json_field(state, "status")
    if (identical(status, "completed")) break
    if (status %in% c("failed", "cancelled")) stop("Redivis's export of ", table, " ", status, ".", call. = FALSE)
    Sys.sleep(min(i * 0.5, 2))
  }
  if (!identical(status, "completed")) stop("Redivis's export of ", table, " did not complete in time.", call. = FALSE)
  n <- as.integer(.erw_json_field(state, "fileCount"))
  parts <- lapply(seq_len(max(n, 1L)) - 1L, function(k) {
    part <- tempfile(fileext = ".csv")
    .erw_curl(c("-sS", "-f", "-L", auth, "-o", shQuote(part), shQuote(paste0(api, "/exports/", id, "/download?filePart=", k))))
    .erw_read_csv(part)
  })
  do.call(rbind, parts)
}

.erw_redivis_version <- function() {
  token <- Sys.getenv("REDIVIS_API_TOKEN")
  if (!nzchar(token)) return(NA_character_)
  path <- tempfile(fileext = ".json")
  ok <- tryCatch({
    .erw_curl(c("-sS", "-f", "-H", shQuote(paste("Authorization: Bearer", token)), "-o", shQuote(path),
                shQuote("https://redivis.com/api/v1/datasets/datapages.erw:b9wm")))
    TRUE
  }, error = function(e) FALSE)
  if (!ok) return(NA_character_)
  .erw_json_field(path, "tag")
}

.erw_time <- function(x) {
  x <- sub("T", " ", x, fixed = TRUE)
  x <- substr(x, 1L, 19L)
  x <- ifelse(nchar(x) == 10L, paste(x, "00:00:00"), x)
  as.POSIXct(x, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
}

.erw_number <- function(x) suppressWarnings(as.numeric(x))

.erw_types <- function(df, shape) {
  for (c in names(df)) {
    type <- erw_column_type(shape, c)
    if (type == "number") df[[c]] <- .erw_number(df[[c]])
    if (type == "utc time") df[[c]] <- .erw_time(df[[c]])
    if (type == "date") df[[c]] <- as.Date(substr(df[[c]], 1L, 10L))
  }
  df
}

#' The type a column has, by the table's shape (docs/methods/packages.md, "The column types, by shape").
#' @param shape "series", "entities" or "events"
#' @param column a column name
#' @return "number", "utc time", "date" or "text"
#' @export
erw_column_type <- function(shape, column) {
  if (shape == "series") {
    if (column == "value") return("number")
    if (column == "ts_utc") return("utc time")
    return("text")
  }
  if (shape == "entities") {
    if (column %in% c("lat", "lon", "capacity_mw") || endsWith(column, "_mw")) return("number")
    if (column == "status_date" || endsWith(column, "_date")) return("date")
    if (column == "retrieved_at") return("utc time")
    return("text")
  }
  if (shape == "events") {
    if (column == "event_date") return("utc time")
    if (column %in% c("mw", "price", "significance", "ai_power_relevance")) return("number")
  }
  "text"
}

.erw_filter <- function(df, shape, entity = NULL, variable = NULL, start = NULL, end = NULL) {
  cols <- switch(shape, series = c("entity", "variable", "ts_utc"), entities = c("entity_id", "entity_type", "status_date"),
                 c("source", "event_type", "event_date"))
  if (length(entity) > 0) {
    keep <- df[[cols[1]]] %in% entity
    if ("node" %in% names(df)) keep <- keep | df$node %in% entity
    if (shape == "entities" && "name" %in% names(df)) keep <- keep | df$name %in% entity
    df <- df[keep, , drop = FALSE]
  }
  if (length(variable) > 0) df <- df[df[[cols[2]]] %in% variable, , drop = FALSE]
  if (length(start) > 0 || length(end) > 0) {
    t <- df[[cols[3]]]
    if (shape == "entities") t <- as.POSIXct(t, tz = "UTC")
    keep <- !is.na(t)
    if (length(start) > 0) keep <- keep & t >= .erw_time(start)
    if (length(end) > 0) keep <- keep & t < .erw_time(end)
    df <- df[keep, , drop = FALSE]
  }
  rownames(df) <- NULL
  df
}

.erw_route <- function(table, window, start = NULL) {
  dir <- Sys.getenv("ERW_DATA_DIR")
  if (nzchar(dir) && file.exists(file.path(dir, paste0(table, ".csv")))) return("local")
  configured <- nzchar(Sys.getenv("ERW_LIVE_URL", Sys.getenv("SUPABASE_URL"))) &&
    nzchar(Sys.getenv("ERW_LIVE_KEY", Sys.getenv("SUPABASE_ANON_KEY")))
  if (configured && window %in% c("whole", "some rows")) return("live")
  days <- suppressWarnings(as.integer(sub(" days$", "", window)))
  if (configured && !is.na(days) && length(start) > 0 &&
      as.Date(substr(start, 1L, 10L)) >= Sys.Date() - (days - 5L)) return("live")
  "redivis"
}

.erw_license_row <- function(table) {
  lic <- .erw_record("licenses")
  lic[lic$table == table, , drop = FALSE]
}

#' Every table of the warehouse, one row each.
#' @return a data frame: table, shape, interval, ts_min, ts_max, n_rows, verdict, in_live, title
#' @export
erw_tables <- function() {
  cov <- .erw_record("coverage")
  lic <- .erw_record("licenses")
  out <- merge(cov, lic[, c("table", "verdict", "live_window")], by = "table", all.x = TRUE, sort = TRUE)
  rel <- tryCatch(.erw_record("release"), error = function(e) data.frame(table = character(0), description = character(0)))
  titles <- stats::setNames(rel$description, rel$table)
  data.frame(table = out$table,
             shape = ifelse(out$interval == "snapshot", "entities", ifelse(out$interval == "event", "events", "series")),
             interval = out$interval, ts_min = .erw_time(out$ts_min), ts_max = .erw_time(out$ts_max),
             n_rows = .erw_number(out$n_rows), verdict = ifelse(is.na(out$verdict), "", out$verdict),
             in_live = ifelse(is.na(out$live_window) | out$live_window %in% c("", "none"), "no", "yes"),
             title = ifelse(is.na(titles[out$table]), "", titles[out$table]), stringsAsFactors = FALSE, row.names = NULL)
}

#' The coverage row of a table, or every row.
#' @param table a table name, or NULL for every table
#' @export
erw_coverage <- function(table = NULL) {
  cov <- .erw_record("coverage")
  lic <- .erw_record("licenses")
  out <- merge(cov, lic[, c("table", "verdict", "live_window")], by = "table", all.x = TRUE, sort = TRUE)
  for (c in c("n_nodes", "n_rows")) out[[c]] <- .erw_number(out[[c]])
  for (c in c("ts_min", "ts_max", "last_run")) out[[c]] <- .erw_time(out[[c]])
  if (!is.null(table)) {
    out <- out[out$table == table, , drop = FALSE]
    if (nrow(out) == 0) stop(sprintf("No ERW table named %s. erw_tables() lists every table.", table), call. = FALSE)
  }
  rownames(out) <- NULL
  out
}

#' A table's license: its verdict, status, publishers and words.
#' @param table a table name
#' @export
erw_license <- function(table) {
  row <- .erw_license_row(table)
  if (nrow(row) == 0) stop(sprintf("No ERW table named %s. erw_tables() lists every table.", table), call. = FALSE)
  split <- function(x) if (nzchar(x)) trimws(strsplit(x, ";", fixed = TRUE)[[1]]) else character(0)
  list(table = table, verdict = row$verdict[1], status = row$status[1], status_from = row$status_from[1],
       decided_by = split(row$decided_by[1]), publishers = split(row$publishers[1]), words = row$words[1])
}

#' One table's rows.
#' @param table a table name
#' @param entity entities (ercot:HB_NORTH) or nodes (HB_NORTH); an events table's sources; an entities table's ids
#' @param variable variables, entity types or event types
#' @param start,end a UTC window of interval starts, [start, end), as "YYYY-MM-DD" or "YYYY-MM-DDThh:mm:ssZ"
#' @param backend "auto", "local", "live" or "redivis"
#' @return a data frame with the attributes erw_version and erw_license
#' @export
erw_fetch <- function(table, entity = NULL, variable = NULL, start = NULL, end = NULL, backend = "auto") {
  shape <- .erw_shape(table)
  lic <- .erw_license_row(table)
  verdict <- if (nrow(lic)) lic$verdict[1] else ""
  words <- if (nrow(lic)) lic$words[1] else ""
  if (backend == "auto") backend <- .erw_route(table, if (nrow(lic)) lic$live_window[1] else "", start)
  if (!backend %in% c("local", "live", "redivis")) stop("erw: backend is auto, local, live or redivis", call. = FALSE)
  if (nzchar(verdict) && verdict != "public") {
    if (backend != "local") {
      stop(sprintf("%s is not public: %s. %s The ERW's license record: %s", table, verdict, words,
                   "https://github.com/SamuelEnrique/erw/blob/main/docs/licenses.md"), call. = FALSE)
    }
    warning(sprintf("%s is not public (%s): %s Read from local files, your own copy under its own license.",
                    table, verdict, words), call. = FALSE)
  }
  df <- switch(backend,
               local = .erw_read_csv(file.path(Sys.getenv("ERW_DATA_DIR"), paste0(table, ".csv"))),
               live = .erw_live_read(table, shape, entity, variable, start, end),
               redivis = .erw_redivis_read(table))
  df <- .erw_filter(.erw_types(df, shape), shape, entity, variable, start, end)
  if (nrow(df) == 0 && (length(start) > 0 || length(end) > 0)) {
    cov <- .erw_record("coverage")
    row <- cov[cov$table == table, , drop = FALSE]
    message(sprintf("No rows of %s start in [%s, %s); its rows run from %s to %s.", table,
                    if (length(start)) start else "the first row", if (length(end)) end else "the last row",
                    row$ts_min[1], row$ts_max[1]))
  }
  where <- switch(backend, local = "local files", live = "the live set", redivis = "Redivis datapages.erw:b9wm latest release")
  fetched <- format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
  attr(df, "erw_version") <- sprintf("ERW %s: %s; ERW commit unknown; fetched %s; %d rows", table, where, fetched, nrow(df))
  attr(df, "erw_license") <- verdict
  attr(df, "erw_backend") <- backend
  attr(df, "erw_fetched") <- fetched
  df
}

#' The citation line, in the release's words.
#' @param table a table name
#' @param data a data frame erw_fetch() returned, for the clause saying where its rows came from
#' @export
erw_cite <- function(table, data = NULL) {
  src <- .erw_record("sources")
  mig <- .erw_record("migrations")
  wanted <- c(table, mig$old_table[mig$new_table == table])
  names_in <- function(x) trimws(strsplit(x, "[;,]")[[1]])
  hit <- vapply(src$tables, function(x) any(names_in(x) %in% wanted), logical(1))
  pubs <- sort(unique(src$publisher[hit & nzchar(src$publisher)]), method = "radix")
  reps <- sort(unique(src$report[hit & nzchar(src$report)]), method = "radix")
  if (length(pubs) == 0) {
    lic <- .erw_license_row(table)
    pubs <- if (nrow(lic) && nzchar(lic$publishers[1])) lic$publishers[1] else "Energy Research Warehouse (ERW)"
  }
  head <- paste(pubs, collapse = "; ")
  rep <- if (length(reps)) paste0(" ", paste(reps, collapse = "; "), ".") else ""
  backend <- if (is.null(data)) "" else attr(data, "erw_backend")
  clause <- if (identical(backend, "live")) {
    paste0("the live set, fetched ", attr(data, "erw_fetched"))
  } else if (identical(backend, "local")) {
    "local files (no ERW commit identifies them)"
  } else {
    # session 1014: the released version's tag, as Redivis names it (one request), as the Python package cites it
    tag <- .erw_redivis_version()
    paste0("Redivis dataset `datapages.erw`, version ", if (is.na(tag)) "<the version you read>" else tag)
  }
  paste0(head, ".", rep, " Via the Energy Research Warehouse (ERW), table `", table, "`, ", clause, ".")
}

#' A table's shape and columns, each with its type and whether the data standard requires it.
#' @param table a table name
#' @param backend "auto", "local", "live" or "redivis"
#' @export
erw_standard <- function(table, backend = "auto") {
  shape <- .erw_shape(table)
  if (backend == "auto") backend <- .erw_route(table, "whole")
  cols <- switch(backend,
                 local = names(.erw_read_csv(file.path(Sys.getenv("ERW_DATA_DIR"), paste0(table, ".csv")))),
                 live = names(.erw_live_read(table, shape, limit = 1L)),
                 redivis = names(.erw_redivis_read(table, limit = 1L)))
  rules <- switch(shape,
                  series = list(req = c("entity", "variable", "ts_utc", "value"),
                                res = c("unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"),
                                part = c("ba", "year", "event"), key = c("entity", "variable", "ts_utc")),
                  entities = list(req = c("entity_id", "entity_type", "name", "source"),
                                  res = c("geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
                                          "source_url", "retrieved_at", "vintage"), part = character(0), key = "entity_id"),
                  list(req = c("event_id", "event_date", "event_type", "source", "source_url"),
                       res = c("parties", "entity_ids", "mw", "price", "currency", "status"), part = character(0),
                       key = "event_id"))
  need <- ifelse(cols %in% rules$req, "yes", ifelse(cols %in% rules$res, "reserved", ifelse(cols %in% rules$part, "partition", "extra")))
  list(table = table, shape = shape,
       columns = data.frame(name = cols, type = vapply(cols, function(c) erw_column_type(shape, c), character(1)),
                            required = need, stringsAsFactors = FALSE, row.names = NULL),
       key = rules$key)
}

#' The requests this session has made to Redivis and the live set.
#' @export
erw_requests <- function() {
  c(redivis = if (is.null(.erw_state$requests_redivis)) 0L else .erw_state$requests_redivis,
    live = if (is.null(.erw_state$requests_live)) 0L else .erw_state$requests_live)
}
