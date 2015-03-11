/* drop_tables_views.sql
 *
 * drop tables:
 *    high_low, open_close_volume
 *
 * drop views:
 *    high, low, open, close, volume
 */

DROP VIEW IF EXISTS high;
DROP VIEW IF EXISTS low;
DROP VIEW IF EXISTS open;
DROP VIEW IF EXISTS close;
DROP VIEW IF EXISTS volume;

DROP TABLE IF EXISTS high_low;
DROP TABLE IF EXISTS open_close_volume;
