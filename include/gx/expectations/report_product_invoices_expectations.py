from great_expectations.core import ExpectationSuite, ExpectationConfiguration

suite = ExpectationSuite(expectation_suite_name="report_product_invoices_suite")

# All products have a stock code (no nulls)
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "stock_code"}
    )
)

# Total quantity sold is greater than 0
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "total_quantity_sold", "min_value": 1}
    )
)