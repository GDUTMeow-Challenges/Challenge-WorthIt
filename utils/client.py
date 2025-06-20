import json
from datetime import datetime
import uuid

class Client:
    def __init__(self, path):
        self.path = path

    def load(self) -> list:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"Error: The file {self.path} does not exist.")
            return None
        except json.JSONDecodeError:
            print(f"Error: The file {self.path} is not a valid JSON file.")
            return None
        
    def read(self, iid: str) -> dict:
        """
        Read an single item from the JSON file by its ID.
        """
        data = self.load()
        if data is None:
            return None
        for item in data:
            if item.get("id") == iid:
                return item
        print(f"Error: Item with ID {iid} not found.")
        return None

    def save(
        self,
        name: str,
        purchase_price: float,
        additional_price: float,
        entry_date: datetime,
        retire_date: datetime,
        remark: str,
    ) -> bool: 
        try:
            data = self.load()
            if data is None:
                data = []
            data.append({
                "id": str(uuid.uuid4()),
                "name": name,
                "purchase_price": purchase_price,
                "additional_price": additional_price,
                "entry_date": entry_date,
                "retire_date": retire_date if retire_date else None,
                "remark": remark,
            })

            with open(self.path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def edit(
        self,
        iid: str,
        name: str,
        purchase_price: float,
        additional_price: float,
        entry_date: datetime,
        retire_date: datetime,
        remark: str,
    ) -> bool: 
        try:
            data = self.load()
            if data is None:
                return False
            for item in data:
                if item.get("id") == iid:
                    item["name"] = name
                    item["purchase_price"] = purchase_price
                    item["additional_price"] = additional_price
                    item["entry_date"] = entry_date.isoformat()
                    item["retire_date"] = retire_date.isoformat()
                    item["remark"] = remark
                    break
            else:
                print(f"Error: {name} not found in the data.")
                return False

            with open(self.path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def delete(self, item_id: str) -> bool:
        try:
            data = self.load()
            if data is None:
                return False

            new_data = [item for item in data if item.get("id") != item_id]
            if len(new_data) == len(data):
                print(f"Error: Item with ID {item_id} not found.")
                return False
            with open(self.path, "w", encoding="utf-8") as file:
                json.dump(new_data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        