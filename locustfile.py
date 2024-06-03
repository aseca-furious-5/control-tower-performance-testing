from locust import HttpUser, task, between
import random
import string


class UserBehavior(HttpUser):
    wait_time = between(0.5, 2.5)

    @task(5)
    def create_item(self):
        item_name = ''.join(random.choices(string.ascii_letters, k=10))
        item_price = random.randint(1, 1000)
        self.client.post("/item", json={'name': item_name, 'price': item_price})

    @task(1)
    def get_items(self):
        self.client.get("/item/all")

    @task(4)
    def perform_order_operations(self):
        order = {'items': []}
        for i in range(1, random.randint(1, 5)):
            order['items'].append({'id': random.randint(1, 100), 'quantity': 1})

        response = self.create_order(order)
        if response:
            order_id = response.json().get('id')
            if order_id:
                self.get_order(order_id)
                possible_statuses = ['PREPARING', 'READY_TO_DISPATCH', 'DISPATCHED']
                updated_order = {'status': random.choice(possible_statuses)}
                self.edit_order(order_id, updated_order)

    def get_order(self, order_id):
        return self.client.get(f"/order/{order_id}")

    def create_order(self, order):
        response = self.client.post("/order", json=order)
        return response

    def edit_order(self, order_id, order):
        self.client.put(f"/order/{order_id}", json=order)
