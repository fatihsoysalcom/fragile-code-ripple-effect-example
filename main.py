import math

class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

class Order:
    def __init__(self, order_id: str, products: list['Product']):
        self.order_id = order_id
        self.products = products
        # Initial simple total calculation
        self._total_amount = sum(p.price for p in products)

    @property
    def total_amount(self) -> float:
        return self._total_amount

    def get_product_names(self) -> list[str]:
        return [p.name for p in self.products]

# --- Legacy Modules (Fragile Code) ---

class LegacyPaymentProcessor:
    def process_payment(self, order: Order) -> bool:
        print(f"\n--- LegacyPaymentProcessor for Order {order.order_id} ---")
        # PROBLEM: This module directly accesses internal 'products' and recalculates total.
        # It assumes a simple sum of product prices, tightly coupling it to Order's internal structure.
        # If Order's total calculation logic changes (e.g., adds discount), this will be out of sync.
        calculated_total_by_processor = sum(p.price for p in order.products)
        print(f"Processor's internal calculation (based on raw products): ${calculated_total_by_processor:.2f}")
        print(f"Order's official reported total (from property): ${order.total_amount:.2f}")

        # Simulate a critical business rule: The processor's internal calculation MUST match the order's official total.
        # This is where the 'crash' or failure manifests due to the new feature.
        if not math.isclose(calculated_total_by_processor, order.total_amount, rel_tol=1e-9):
            print(f"ERROR: Payment processor's total (${calculated_total_by_processor:.2f}) does not match order's official total (${order.total_amount:.2f}).")
            print("This indicates a critical inconsistency caused by a change in order logic.")
            return False # Payment failed due to inconsistency

        print(f"Processing payment for {order.order_id} with total: ${order.total_amount:.2f}")
        if order.total_amount > 0:
            print(f"Payment successful for ${order.total_amount:.2f}.")
            return True
        print("Payment failed: Total amount is zero or negative.")
        return False

class LegacyReportingModule:
    def generate_report(self, order: Order):
        print(f"\n--- LegacyReportingModule for Order {order.order_id} ---")
        print(f"Order ID: {order.order_id}")
        print("Products:")
        for product in order.products:
            print(f"  - {product.name}: ${product.price:.2f}")
        # PROBLEM: This module relies on 'order.total_amount'. If the property was removed,
        # or its type changed unexpectedly, this module would crash. It's fragile due to direct reliance.
        print(f"Reported Total Amount (from order property): ${order.total_amount:.2f}")
        print("Report generated.")

# --- Main Execution ---

if __name__ == "__main__":
    print("Scenario 1: Initial System (before new feature)")

    product1 = Product("Laptop", 1200.00)
    product2 = Product("Mouse", 25.00)
    initial_order = Order("ORD-001", [product1, product2])

    payment_processor = LegacyPaymentProcessor()
    reporting_module = LegacyReportingModule()

    print("\nRunning legacy modules with initial order:")
    payment_processor.process_payment(initial_order)
    reporting_module.generate_report(initial_order)

    print("\n" + "="*80)
    print("Scenario 2: Introducing a 'New Feature' - Modifying Order's Total Calculation")
    print("Imagine we need to add a discount mechanism to orders.")

    # --- THE "NEW FEATURE" / CHANGE ---
    # We simulate modifying the Order class to include a discount and update total_amount calculation.
    # This change is internal to Order, but it has ripple effects on tightly coupled modules.

    class OrderWithDiscount(Order): # Simulates modifying the original Order class
        def __init__(self, order_id: str, products: list['Product'], discount_percentage: float = 0.0):
            super().__init__(order_id, products)
            self.discount_percentage = discount_percentage
            # NEW FEATURE: Update total_amount calculation to include discount
            self._total_amount = sum(p.price for p in products) * (1 - self.discount_percentage / 100)
            self._total_amount = round(self._total_amount, 2) # Ensure clean float

    product3 = Product("Keyboard", 75.00)
    product4 = Product("Monitor", 300.00)
    new_feature_order = OrderWithDiscount("ORD-002", [product3, product4], discount_percentage=10.0)

    print(f"\nNew Order (with 10% discount): {new_feature_order.order_id}")
    print(f"Expected discounted total: ${new_feature_order.total_amount:.2f}")

    print("\nRunning legacy modules with the new order (which uses the modified Order class):")
    # The legacy modules are unaware of the discount logic.
    # The Payment Processor will now detect an inconsistency and "crash" (fail).
    payment_processor.process_payment(new_feature_order)
    reporting_module.generate_report(new_feature_order)

    print("\n--- Analysis of the 'Crash' / Inconsistency ---")
    print("The LegacyPaymentProcessor detected a mismatch between its internal calculation (undiscounted)")
    print("and the Order's official total (discounted). This led to a payment failure,")
    print("demonstrating how a seemingly isolated change in the 'Order' class's logic")
    print("can cause critical failures in other tightly coupled modules.")
    print("The 'crash' here is a logical failure preventing a core business process (payment) from completing correctly.")
    print("The LegacyReportingModule, while not crashing, might also be considered fragile if 'total_amount'")
    print("was removed or drastically changed its meaning/type.")
