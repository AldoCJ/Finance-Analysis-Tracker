from rapidfuzz import process
import json

with open('categories.json', 'r') as file:
    category_data = json.load(file)

class Purchase:
    def __init__(self, date, label, amount):
        self.date = date
        self.label = label
        self.amount = amount
        self.category = "Other"


    def set_category(self, ask_user_callback):
        categories = category_data["categories"]
        merchants_categories = category_data["merchants"]

        desc = self.label.lower()

        best_match, score, _ =  process.extractOne(desc, merchants_categories.keys())
        
        if best_match and score >= 75:
            self.category = merchants_categories[best_match]
        else:
            self.category = ask_user_callback(self.label, categories)

            merchants_categories[desc] = self.category
            try:
                with open('categories.json', 'w') as file:
                    json.dump(category_data, file, indent=4)
            except Exception as e:
                print (f"Error updating categories.json: {e}")


class Deposit:
    def __init__(self, date, amount):
        self.date = date
        self.amount = amount

class MonthData:
    def __init__(self, month):
        self.month = month
        self.total_spent = 0.0
        self.total_earned = 0.0
        self.categories = {cat: 0.0 for cat in category_data["categories"]}

    def to_dict(self):
        return {
            "month": self.month,
            "total_spent": self.total_spent,
            "total_earned": self.total_earned,
            "categories": self.categories
        }

    def load_dict(self, data):
        self.month = (data["month"])
        self.total_spent = data["total_spent"]
        self.total_earned = data["total_earned"]
        self.categories = data["categories"]

    def add_purchase(self, purchase):
        self.total_spent += purchase.amount
        print("Here")
        self.categories[purchase.category] += purchase.amount
        self.clean_data()

    def add_deposit(self, deposit):
        self.total_earned += deposit.amount
        self.clean_data()

    def clean_data(self):
        self.total_earned = int(self.total_earned * 100) / 100
        self.total_spent = int(self.total_spent * 100) / 100

    def data_exists(self):
        return (self.total_earned != 0 or self.total_spent != 0)
    
    
class YearData:
    def __init__(self, year):
        self.year = year
        self.total_spent = 0.0
        self.total_earned = 0.0
        self.average_spending = 0.0
        self.average_earning = 0.0
        self.months = []
        self.categories= {cat: 0.0 for cat in category_data["categories"]}
        self.init_months()

    def init_months(self):
        months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
        
        self.months = [MonthData(month) for month in months]
    
    def to_dict(self):
        return {
            "year": self.year,
            "total_spent": self.total_spent,
            "total_earned": self.total_earned,
            "average_spending": self.average_spending,
            "average_earning": self.average_earning,
            "months" : [month.to_dict() for month in self.months],
            "categories": self.categories
        }
    
    def load_dict(self, data):
        self.year = (data["year"])
        self.total_spent = data["total_spent"]
        self.total_earned = data["total_earned"]
        self.average_earning = data["average_earning"]
        self.average_spending = data["average_spending"]
        self.categories = data["categories"]

        index = 0
        for month in data["months"]:
            self.months[index].load_dict(month)
            index += 1

    def add_purchases(self, purchases, ask_user_callback):
        print(self.categories)
        for purchase in purchases:
            purchase.set_category(ask_user_callback)
            self.categories[purchase.category] += purchase.amount
            index = int(purchase.date.split('/')[0]) - 1
            
            self.months[index].add_purchase(purchase)
        
        self.average_spending = 0.0
        valid_months = 0

        for month in self.months:
            if month.data_exists():
                self.average_spending += month.total_spent
                valid_months += 1
        self.total_spent = self.average_spending
        self.average_spending /= valid_months
        self.clean_data()
        
    def add_deposits(self, deposits):
        for deposit in deposits:
            index = int(deposit.date.split('/')[0]) - 1
            self.months[index].add_deposit(deposit)

        self.average_earning = 0
        valid_months = 0
        
        for month in self.months:
            if month.data_exists():
                self.average_earning += month.total_earned
                valid_months += 1
        self.total_earned = self.average_earning
        self.average_earning /= valid_months
        self.clean_data()

    def clean_data(self):
        self.total_earned = int(self.total_earned * 100) / 100
        self.total_spent = int(self.total_spent * 100) / 100
        self.average_earning = int(self.average_earning * 100) / 100
        self.average_spending = int(self.average_spending * 100) / 100

class AllData:
    def __init__(self):
        self.years = []

    def load_data(self, data):
        for item in data:
            year_data = YearData(item["year"])
            year_data.load_dict(item)
            self.years.append(year_data)

    def add_data(self, purchases, deposits, year, ask_user_callback):
        for item in self.years:
            if item.year == year:
                item.add_purchases(purchases, ask_user_callback)
                item.add_deposits(deposits)
                return
            
        new_year = YearData(year)
        new_year.add_purchases(purchases, ask_user_callback)
        new_year.add_deposits(deposits)
        self.years.append(new_year)
    
    def add_year(self, year):
        self.years.append(YearData(year))

    def save_data(self):
        return [year.to_dict() for year in self.years]
    
    def get_years(self):
        return [year.year for year in self.years]

   