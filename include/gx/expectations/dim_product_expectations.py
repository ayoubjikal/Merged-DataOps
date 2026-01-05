from great_expectations.core import ExpectationSuite, ExpectationConfiguration

suite = ExpectationSuite(expectation_suite_name="dim_product_suite")

# Schema: Required columns
required_columns = ["product_id", "description", "price"]
for col in required_columns:
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_to_exist",
            kwargs={"column": col}
        )
    )

# Schema: Column types
column_types = {
    "product_id": "str",
    "description": "str",
    "price": "float64",
}
for col, dtype in column_types.items():
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={"column": col, "type_": dtype}
        )
    )

# All products are unique
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_unique",
        kwargs={"column": "product_id"}
    )
)

# All products have a key (no nulls)
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "product_id"}
    )
)

# All prices are non-negative
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "price", "min_value": 0}
    )
)