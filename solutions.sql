use macro;

select * from macro_data_25yrs
limit 10;

select * from spy_close
limit 10;

-- 1. How many years of data, what's the data frequency
select distinct(Year(Date)) from macro_data_25yrs;

-- 2. Any missing values
select 
	sum(case when M2_Money_Supply is null then 1 else 0 end) M2_Money_Supply_na,
    sum(case when `10Y Treasury Yield` is null then 1 else 0 end) 10Y_Yield_na,
    sum(case when `Fed Funds Rate` is null then 1 else 0 end) Fed_Funds_Rate_na,
    sum(case when CPI is null then 1 else 0 end) CPI_na,
    sum(case when `Inflation_Rate_%` is null then 1 else 0 end) Inflation_Rate_na,
    sum(case when SOFR is null then 1 else 0 end) SOFR_na
from macro_data_25yrs;

-- 3. Average of each column
select 
	avg(M2_Money_Supply) as M2_Money_Supply_avg,
    avg(`10Y Treasury Yield`) as 10Y_Yield_avg,
    avg(`Fed Funds Rate`) as Fed_Fund_Rate_avg,
    avg(CPI) as CPI_avg,
    avg(`Inflation_Rate_%`) as Inflation_Rate_avg,
    avg(SOFR) as SOFR_avg
from macro_data_25yrs;

-- 4. How CPI and M2_Money_Supply associate with Inflation_Rate_%
select 
	avg(CPI),
    avg(M2_Money_Supply)
from macro_data_25yrs
where `Inflation_Rate_%` <2;

select 
	avg(CPI),
    avg(M2_Money_Supply)
from macro_data_25yrs
where `Inflation_Rate_%`>=2 and `Inflation_Rate_%` <4;

select 
	avg(CPI),
    avg(M2_Money_Supply)
from macro_data_25yrs
where `Inflation_Rate_%`>=4 and `Inflation_Rate_%` <6;

-- 5. avg 1m return of SPY
select avg(F1M_Return) from spy_close;

-- 6. count % days that SPY has higher than avg return
select 
	count(*) / (select count(*) from spy_close)
from spy_close
where F1M_Return > (select avg(F1M_Return) from spy_close);


-- 7. How 1m return associates with Inflation_Rate_%
select
	avg(F1M_Return)
from (
	select
		m.`Inflation_Rate_%` as inf,
        s.F1M_Return
	from macro_data_25yrs m
    left join spy_close s on m.Date = s.Date
) macro_spy
where inf < 2;

select
	avg(F1M_Return)
from (
	select
		m.`Inflation_Rate_%` as inf,
        s.F1M_Return
	from macro_data_25yrs m
    left join spy_close s on m.Date = s.Date
) macro_spy
where inf >=2 and inf < 4;

-- 8. How 1m return associates with 10Y Yield
select
	avg(F1M_Return)
from (
	select
		m.`10Y Treasury Yield` as 10y_yield,
        s.F1M_Return
	from macro_data_25yrs m
    left join spy_close s on m.Date = s.Date
) macro_spy
where 10y_yield < 1;

select
	avg(F1M_Return)
from (
	select
		m.`10Y Treasury Yield` as 10y_yield,
        s.F1M_Return
	from macro_data_25yrs m
    left join spy_close s on m.Date = s.Date
) macro_spy
where 10y_yield >=1 and 10y_yield < 2;




