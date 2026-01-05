from great_expectations.core import ExpectationSuite, ExpectationConfiguration

suite = ExpectationSuite(expectation_suite_name="raw_invoices_suite")

# Schema: Required columns exist
required_columns = ["InvoiceNo", "StockCode", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]
for col in required_columns:
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_to_exist",
            kwargs={"column": col}
        )
    )

# Schema: Column types
column_types = {
    "InvoiceNo": "str",
    "StockCode": "str",
    "Quantity": "int64",
    "InvoiceDate": "str",
    "UnitPrice": "float64",
    "CustomerID": "float64",
    "Country": "str",
}
for col, dtype in column_types.items():
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={"column": col, "type_": dtype}
        )
    )