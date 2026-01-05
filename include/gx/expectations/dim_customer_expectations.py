from great_expectations.core import ExpectationSuite, ExpectationConfiguration

suite = ExpectationSuite(expectation_suite_name="dim_customer_suite")

# Schema: Required columns
required_columns = ["customer_id", "country"]
for col in required_columns:
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_to_exist",
            kwargs={"column": col}
        )
    )

# Schema: Column types
column_types = {
    "customer_id": "str",
    "country": "str",
}
for col, dtype in column_types.items():
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={"column": col, "type_": dtype}
        )
    )

# All customers are unique
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_unique",
        kwargs={"column": "customer_id"}
    )
)

# All customers have a key (no nulls)
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "customer_id"}
    )
)