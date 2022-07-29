class Generator(object):

    """
    Generator class generates common sql insert, update, delete,
    select along with where clause.
    It expects the payloads which further supplies the reqd information
    to the specific methods.

    """

    def __init__(self, payload):
        self.payload = payload

    def delete_query(self):
        query = """del from {table_name} where {target_column}=%s""".format(
            table_name=self.payload["TableName"],
            target_column=self.payload["TargetColumn"],
        )

    def insert_query(self, columns, data_type):

        # create the dynamic insert query.
        insert_query = (
            "INSERT INTO {table} ".format(table=self.payload["TableName"])
            + "VALUES "
            + "{data_type}".format(data_type=data_type)
        )
        print(insert_query)
        return insert_query

    def col_query(self, *data_type, db_type=None):

        if data_type:
            column_query = """
            SELECT column_name,data_type FROM INFORMATION_SCHEMA. COLUMNS WHERE TABLE_NAME=%s order by ORDINAL_POSITION;
            """
        else:
            column_query = """
                    SELECT column_name FROM INFORMATION_SCHEMA. COLUMNS WHERE TABLE_NAME=%s order by ORDINAL_POSITION;
                    """

        if db_type:
            column_query = """
             SELECT column_name
                FROM   v_catalog.columns
                WHERE  table_schema=%s
                    AND table_name=%s
                ORDER  BY ordinal_position"""

        return column_query

    def select_query(self):
        query = "select * from {schema}.{table_name}".format(
            schema=self.payload["Schema"], table_name=self.payload["TableName"]
        )

        return query
