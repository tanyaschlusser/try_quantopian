#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
group_data_by_columns.py

The order of the columns is:
    date, <blank>, open, high, low, close, volume

The goal is to split out 
"""
import glob
import os
import pandas as pd


# ----------------------------------------------- Ingestion ----- #
colnames = ['open', 'high', 'low', 'close', 'volume']
OCV = "open_close_volume"
HL = "high_low"
ocv_df = pd.DataFrame(columns=['date'])
hl_df = pd.DataFrame(columns=['date'])

for fname in glob.glob(os.path.join(
        "data", "quantquote_daily_sp500_83986", "daily", "*")):
    prefix = fname.rsplit('_', 1)[-1].split('.')[0]
    names = ['date', 'blank'] + [prefix + '_' + c for c in colnames]
    df = pd.read_csv(fname, names=names)
    ocv_df = ocv_df.merge(
            df.ix[:,[names[n] for n in (0,2,5,6)]],
            how='outer',
            on='date')
    hl_df = hl_df.merge(
            df.ix[:,[names[n] for n in (0,3,4)]],
            how='outer',
            on='date')


# Convert the date format to ISO (YYYY-MM-DD)
def convert_date(yyyymmdd):
    ymd = str(int(yyyymmdd))
    return "-".join((ymd[0:4], ymd[4:6], ymd[6:8]))

ocv_df["date"] = ocv_df["date"].apply(convert_date)
hl_df["date"] = hl_df["date"].apply(convert_date)
SOURCES = {OCV:ocv_df, HL:hl_df}


# Output
ocv_df.to_csv(os.path.join("data", OCV + ".csv"), index=False)
hl_df.to_csv( os.path.join("data", HL + ".csv"), index=False)


# ------------------------------------------- Create Tables ----- #
boilerplate = (
        "/* {}"
        " *"
        " * Automatically generated create statements from"
        " * group_data_by_columns.py for the s&p500 stock"
        " * dataset on https://quantquote.com/historical-stock-data"
        " */\n\n")

fname = "generated__create_tables.sql"
with open(os.path.join("sql", fname), "w") as outfile:
    outfile.write(boilerplate.format(fname))
    outfile.write((
            "CREATE TABLE IF NOT EXISTS {} (\n"
            "    dt date NOT NULL PRIMARY KEY,\n").format(OCV))
    outfile.write(",\n    ".join("{} real".format(c)
            for c in list(ocv_df.columns.values)[1:]))
    outfile.write(");\n\n")
    outfile.write((
            "CREATE TABLE IF NOT EXISTS {} (\n"
            "    dt date NOT NULL PRIMARY KEY,\n").format(HL))
    outfile.write(",\n    ".join("{} real".format(c)
            for c in list(hl_df.columns.values)[1:]))
    outfile.write(");\n\n")


# --------------------------------------------------- Views ----- #
def create_view(sourcename, destination, col=None):
    source = SOURCES[sourcename]
    if not col:
        col = destination
    outfile.write((
            "CREATE OR REPLACE VIEW {} AS\n"
            "    SELECT dt,\n").format(destination))
    outfile.write(",\n".join(
            "        {{0}}_{} AS {{0}}".format(col).format(c.split("_")[0])
            for c in list(source.columns.values)[1:]
            if c.endswith(col)))
    outfile.write("\nFROM {};\n\n".format(sourcename))


fname = "generated__create_single_datatype_views.sql"
with open(os.path.join("sql", fname), "w") as outfile:
    outfile.write(boilerplate.format(fname))
    create_view(HL, "high")
    create_view(HL, "low")
    create_view(OCV, "open")
    create_view(OCV, "close")
    create_view(OCV, "volume")
    

# --------------------------------------------------- Views ----- #
fname = "generated__insert_data.sql"
with open(os.path.join("sql", fname), "w") as outfile:
    outfile.write(boilerplate.format(fname))
    outfile.write((
            "/* NOTE: \n"
            " *     Run this from above the sql and data directories,\n"
            " *     in the main project directory.\n */\n\n"))
    outfile.write((
        "\\COPY {0} FROM 'data/{0}.csv'"
        "  WITH (FORMAT CSV, NULL '', HEADER)\n\n").format(OCV))
    outfile.write((
        "\\COPY {0} FROM 'data/{0}.csv'"
        "  WITH (FORMAT CSV, NULL '', HEADER)\n").format(HL))

