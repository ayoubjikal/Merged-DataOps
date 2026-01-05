from great_expectations.core import ExpectationSuite, ExpectationConfiguration

suite = ExpectationSuite(expectation_suite_name="dim_datetime_suite")

# Schema: Required columns
required_columns = ["datetime_id", "datetime"]
for col in required_columns:
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_to_exist",
            kwargs={"column": col}
        )
    )

# Schema: Column types
column_types = {
    "datetime_id": "str",
    "datetime": "datetime64",
}
for col, dtype in column_types.items():
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={"column": col, "type_": dtype}
        )
    )

# All weekdays are in range 0-6
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "weekday", "min_value": 0, "max_value": 6}
    )
)

# All datetimes are unique
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_unique",
        kwargs={"column": "datetime_id"}
    )
)

# All datetimes have a key (no nulls)
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "datetime_id"}
    )
)