/* insert_data.sql * * Automatically generated create statements from * group_data_by_columns.py for the s&p500 stock * dataset on https://quantquote.com/historical-stock-data */

/* NOTE: 
 *     Run this from above the sql and data directories,
 *     in the main project directory.
 */

\COPY open_close_volume FROM 'data/open_close_volume.csv'  WITH (FORMAT CSV, NULL '', HEADER)

\COPY high_low FROM 'data/high_low.csv'  WITH (FORMAT CSV, NULL '', HEADER)
