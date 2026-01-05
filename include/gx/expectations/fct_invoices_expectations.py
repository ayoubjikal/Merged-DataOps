from great_expectations.core import ExpectationSuite, ExpectationConfiguration

suite = ExpectationSuite(expectation_suite_name="fct_invoices_suite")

# Schema: Required columns
required_columns = ["invoice_id", "product_id", "customer_id", "datetime_id", "quantity", "total"]
for col in required_columns:
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_to_exist",
            kwargs={"column": col}
        )
    )

# Schema: Column types
column_types = {
    "invoice_id": "str",
    "product_id": "str",
    "customer_id": "str",
    "datetime_id": "str",
    "quantity": "int64",
    "total": "float64",
}
for col, dtype in column_types.items():
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={"column": col, "type_": dtype}
        )
    )

# All invoices have a key (no nulls)
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "invoice_id"}
    )
)

# All invoices have a positive total amount
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "total", "min_value": 0, "strict_min": False}
    )
)