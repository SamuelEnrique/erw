# Session 1005 (chain 070): the R package against the ten real answers of the live set recorded in session 1003
# (fixtures/, the Stata package's own): the address built for each call is the one the Python package requested, and
# each answer reads with the specification's types. No request.

fixture_dir <- test_path("fixtures")
calls <- local({
  txt <- paste(readLines(file.path(fixture_dir, "calls.json"), warn = FALSE), collapse = "\n")
  starts <- gregexpr('"n": [0-9]+', txt)[[1]]
  lapply(seq_along(starts), function(i) {
    one <- substr(txt, starts[i], if (i < length(starts)) starts[i + 1] - 1 else nchar(txt))
    field <- function(name) {
      m <- regmatches(one, regexpr(sprintf('"%s": \\[[^]]*\\]|"%s": "[^"]*"', name, name), one))
      if (!length(m)) return(NULL)
      vals <- regmatches(m, gregexpr('"[^"]*"', m))[[1]][-1]
      gsub('"', "", vals)
    }
    list(table = field("table"), entity = field("entity"), variable = field("variable"), start = field("start"),
         end = field("end"), address = field("addresses")[1], file = field("file"),
         rows = as.integer(sub('.*"csv_rows": ([0-9]+).*', "\\1", one)))
  })
})

shape_of <- function(cols) {
  if (identical(cols[1:2], c("entity_id", "entity_type"))) "entities" else if (cols[1] == "event_id") "events" else "series"
}

test_that("the ten addresses are the Python package's", {
  expect_equal(length(calls), 10)
  for (c in calls) {
    df <- erw:::.erw_read_csv(file.path(fixture_dir, c$file))
    shape <- shape_of(setdiff(names(df), "table_name"))
    url <- erw:::.erw_live_url(c$table, "<ERW_LIVE_URL>", shape, c$entity, c$variable, c$start, c$end)
    expect_equal(url, c$address, info = c$file)
  }
})

test_that("each answer reads with the specification's types", {
  for (c in calls) {
    df <- erw:::.erw_read_csv(file.path(fixture_dir, c$file))
    expect_equal(nrow(df), c$rows, info = c$file)
    shape <- shape_of(setdiff(names(df), "table_name"))
    typed <- erw:::.erw_types(df, shape)
    if (shape == "series") {
      expect_true(is.numeric(typed$value))
      expect_s3_class(typed$ts_utc, "POSIXct")
      expect_false(anyNA(typed$ts_utc))
    }
    if (shape == "events") expect_s3_class(typed$event_date, "POSIXct")
    if (shape == "entities") {
      expect_true(is.numeric(typed$capacity_mw))
      expect_s3_class(typed$status_date, "Date")
    }
  }
})

test_that("fixture 01 is Henry Hub in 2025, as the live set gave it", {
  df <- erw:::.erw_types(erw:::.erw_read_csv(file.path(fixture_dir, "01_eia_fuel_spot_prices.csv")), "series")
  expect_equal(nrow(df), 247)
  expect_equal(df$value[1], 3.65)
  expect_equal(format(df$ts_utc[1], "%Y-%m-%d", tz = "UTC"), "2025-01-02")
})

test_that("the column rule", {
  expect_equal(erw_column_type("series", "value"), "number")
  expect_equal(erw_column_type("series", "retrieved_at"), "text")
  expect_equal(erw_column_type("entities", "net_summer_mw"), "number")
  expect_equal(erw_column_type("entities", "status_date"), "date")
  expect_equal(erw_column_type("events", "event_date"), "utc time")
})
