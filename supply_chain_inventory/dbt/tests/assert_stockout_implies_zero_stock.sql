-- A week flagged as a stockout must end with no stock.
--
-- The source sets the flag when demand exceeded what was on hand, then clamps
-- the balance to zero, so this direction is an invariant. The reverse is not:
-- a week can end at exactly zero without a stockout when demand happened to
-- match stock exactly, which is why this test only checks one direction.
--
-- This is the test that caught the original cleaning bug. Taking abs() of a
-- negative reading turned true stockouts into weeks with one unit in stock,
-- because the defect the generator injects is -value - 1, not a sign flip.

select
    product_id,
    snapshot_date,
    stock_on_hand,
    is_stockout

from {{ ref('fct_inventory_weekly') }}
where is_stockout
  and stock_on_hand > 0
