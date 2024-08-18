from databases import Database

class AppDB:
    def __init__(self, DATABASE_URL):
        self.database = Database(DATABASE_URL)

    async def connect(self):
        await self.database.connect()

    async def save_new_data(self, bcode, pname, quantity, cost):
        await self.database.execute(f"INSERT INTO products(bcode, pname, quantity, cost) " 
                                    f"VALUES (:bcode, :pname, :quantity, :cost)",
                                    values={'bcode': bcode, 'pname': pname, 'quantity': quantity, 'cost': cost})
        
    async def renew_data(self, bcode, pname, quantity, cost):
        await self.database.execute(f"UPDATE products SET (pname, quantity, cost) = (:pname, :quantity, :cost) "
                                    f"WHERE bcode = (:bcode)", 
                                    values={'bcode': bcode, 'pname': pname, 'quantity': quantity, 'cost': cost})
        
    async def renew_quantity(self, bcode, quantity):
        await self.database.execute(f"UPDATE products SET quantity = (:quantity) WHERE bcode = (:bcode)",
                                    values={'bcode': bcode, 'quantity': quantity})
    
    async def get_item_data(self, bcode):
        results = await self.database.fetch_all(f"SELECT * FROM products "
                                                f"WHERE bcode = (:bcode)", values={'bcode': bcode})
        return results
    
    async def get_item_quantity(self, bcode):
        result = await self.database.fetch_val(f"SELECT quantity FROM products where bcode = (:bcode)", values={'bcode': bcode})
        return result