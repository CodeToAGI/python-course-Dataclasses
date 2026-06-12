"""
╔══════════════════════════════════════════════════════════════════╗
║  CodeToAGI — Episode 22 Challenge Solution                       ║
║  Topic: Dataclasses                                              ║
║  Challenge: Build a Product Catalog with @dataclass              ║
╚══════════════════════════════════════════════════════════════════╝

CHALLENGE REQUIREMENTS:
  Step 1 — Category dataclass with frozen=True
  Step 2 — Product dataclass with name, price, quantity, category, tags
  Step 3 — __post_init__ to validate price and quantity
  Step 4 — Catalog dataclass with add, remove, search_by_category methods
  Step 5 — mypy --strict → 0 errors

HOW TO RUN:
  pip install mypy
  python ep22_challenge.py
  mypy --strict ep22_challenge.py
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ─────────────────────────────────────────────────────────────────
# Step 1 — Category (frozen=True → immutable + hashable)
# ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class Category:
    """Immutable product category — safe to use as dict key or in a set."""
    name: str
    description: str = ""

    def __str__(self) -> str:
        return self.name


# ─────────────────────────────────────────────────────────────────
# Step 2 & 3 — Product (validated + derived field)
# ─────────────────────────────────────────────────────────────────

@dataclass(order=True)
class Product:
    """
    A catalog product with typed fields, validation, and a derived total_value.

    Ordering is based on field declaration order:
    sort_index (hidden) → name → price → quantity → ...
    We use sort_index to control sort key cleanly.
    """
    name: str
    price: float
    quantity: int
    category: Category
    tags: List[str] = field(default_factory=list)
    description: str = ""

    # Derived field — not part of __init__, computed in __post_init__
    total_value: float = field(default=0.0, init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        """Validate inputs and compute derived fields."""
        if self.price < 0:
            raise ValueError(f"Product '{self.name}': price must be >= 0, got {self.price}")
        if self.quantity < 0:
            raise ValueError(f"Product '{self.name}': quantity must be >= 0, got {self.quantity}")
        # Use object.__setattr__ not needed here since Product is not frozen
        self.total_value = round(self.price * self.quantity, 2)

    def restock(self, amount: int) -> None:
        """Add stock and recompute total_value."""
        if amount < 0:
            raise ValueError("Restock amount must be >= 0")
        self.quantity += amount
        self.total_value = round(self.price * self.quantity, 2)

    def apply_discount(self, percent: float) -> None:
        """Apply a percentage discount (0–100) and recompute total_value."""
        if not (0 <= percent <= 100):
            raise ValueError("Discount percent must be between 0 and 100")
        self.price = round(self.price * (1 - percent / 100), 2)
        self.total_value = round(self.price * self.quantity, 2)

    def __str__(self) -> str:
        return (
            f"{self.name} | ${self.price:.2f} x {self.quantity} units "
            f"= ${self.total_value:.2f} | [{self.category}]"
        )


# ─────────────────────────────────────────────────────────────────
# Step 4 — Catalog
# ─────────────────────────────────────────────────────────────────

@dataclass
class Catalog:
    """
    A product catalog with add, remove, and search methods.
    All products are stored in a typed List[Product].
    """
    name: str
    products: List[Product] = field(default_factory=list)

    # ── Mutating methods ──────────────────────────────────────────

    def add_product(self, product: Product) -> None:
        """Add a product. Raises ValueError if name already exists."""
        if self._find_by_name(product.name) is not None:
            raise ValueError(f"Product '{product.name}' already exists in catalog.")
        self.products.append(product)

    def remove_product(self, name: str) -> Optional[Product]:
        """Remove a product by name. Returns the removed product or None."""
        for i, p in enumerate(self.products):
            if p.name.lower() == name.lower():
                return self.products.pop(i)
        return None

    # ── Search methods ────────────────────────────────────────────

    def search_by_category(self, category: Category) -> List[Product]:
        """Return all products in the given category."""
        return [p for p in self.products if p.category == category]

    def search_by_tag(self, tag: str) -> List[Product]:
        """Return all products that have the given tag."""
        return [p for p in self.products if tag.lower() in [t.lower() for t in p.tags]]

    def search_by_name(self, query: str) -> List[Product]:
        """Case-insensitive partial name search."""
        return [p for p in self.products if query.lower() in p.name.lower()]

    def in_stock(self) -> List[Product]:
        """Return products with quantity > 0."""
        return [p for p in self.products if p.quantity > 0]

    def out_of_stock(self) -> List[Product]:
        """Return products with quantity == 0."""
        return [p for p in self.products if p.quantity == 0]

    def sorted_by_price(self, descending: bool = False) -> List[Product]:
        """Return products sorted by price."""
        return sorted(self.products, key=lambda p: p.price, reverse=descending)

    def sorted_by_name(self) -> List[Product]:
        """Return products sorted alphabetically by name."""
        return sorted(self.products, key=lambda p: p.name.lower())

    # ── Aggregate stats ───────────────────────────────────────────

    def total_inventory_value(self) -> float:
        """Sum of total_value across all products."""
        return round(sum(p.total_value for p in self.products), 2)

    def most_valuable(self) -> Optional[Product]:
        """Return the product with the highest total_value."""
        return max(self.products, key=lambda p: p.total_value, default=None)

    def cheapest(self) -> Optional[Product]:
        """Return the product with the lowest price."""
        return min(self.products, key=lambda p: p.price, default=None)

    # ── Display ───────────────────────────────────────────────────

    def summary(self) -> str:
        lines = [
            f"╔══ {self.name} ({'empty' if not self.products else f'{len(self.products)} products'}) ══",
            f"║  Total inventory value : ${self.total_inventory_value():,.2f}",
            f"║  In stock              : {len(self.in_stock())}",
            f"║  Out of stock          : {len(self.out_of_stock())}",
            "╠══ Products:",
        ]
        for p in self.sorted_by_name():
            stock_flag = "✓" if p.quantity > 0 else "✗ OUT"
            lines.append(f"║  [{stock_flag}] {p}")
        lines.append("╚" + "═" * 50)
        return "\n".join(lines)

    # ── Private helpers ───────────────────────────────────────────

    def _find_by_name(self, name: str) -> Optional[Product]:
        for p in self.products:
            if p.name.lower() == name.lower():
                return p
        return None


# ─────────────────────────────────────────────────────────────────
# Demo — run this file to see everything in action
# ─────────────────────────────────────────────────────────────────

def main() -> None:
    # --- Categories ---
    electronics = Category(name="Electronics", description="Gadgets and devices")
    books       = Category(name="Books",       description="Physical and digital books")
    clothing    = Category(name="Clothing",    description="Apparel and accessories")

    # --- Products ---
    laptop = Product(
        name="Laptop Pro 15",
        price=1299.99,
        quantity=10,
        category=electronics,
        tags=["laptop", "computer", "work"],
        description="High-performance laptop for developers",
    )
    headphones = Product(
        name="Wireless Headphones",
        price=89.99,
        quantity=50,
        category=electronics,
        tags=["audio", "wireless"],
    )
    python_book = Product(
        name="Python Crash Course",
        price=34.99,
        quantity=200,
        category=books,
        tags=["python", "programming", "beginner"],
    )
    clean_code = Product(
        name="Clean Code",
        price=39.99,
        quantity=0,          # out of stock
        category=books,
        tags=["programming", "best-practices"],
    )
    hoodie = Product(
        name="CodeToAGI Hoodie",
        price=49.99,
        quantity=30,
        category=clothing,
        tags=["merch", "clothing"],
    )

    # --- Catalog ---
    catalog = Catalog(name="CodeToAGI Store")
    for p in [laptop, headphones, python_book, clean_code, hoodie]:
        catalog.add_product(p)

    # --- Display ---
    print(catalog.summary())

    print("\n📦 Electronics only:")
    for p in catalog.search_by_category(electronics):
        print(f"   {p}")

    print("\n🔍 Search 'python':")
    for p in catalog.search_by_name("python"):
        print(f"   {p}")

    print("\n🏷  Tag: 'programming':")
    for p in catalog.search_by_tag("programming"):
        print(f"   {p}")

    print("\n❌ Out of stock:")
    for p in catalog.out_of_stock():
        print(f"   {p.name}")

    print("\n💰 Sorted by price (low → high):")
    for p in catalog.sorted_by_price():
        print(f"   ${p.price:.2f}  {p.name}")

    print(f"\n🏆 Most valuable product: {catalog.most_valuable()}")
    print(f"💲 Cheapest product     : {catalog.cheapest()}")

    # --- Mutations ---
    print("\n🔄 Applying 10% discount to Laptop Pro 15...")
    laptop.apply_discount(10)
    print(f"   New price: ${laptop.price:.2f}  |  New total: ${laptop.total_value:.2f}")

    print("\n📥 Restocking Clean Code (+100 units)...")
    clean_code.restock(100)
    print(f"   {clean_code}")

    print(f"\n🗑  Removing 'CodeToAGI Hoodie'...")
    removed = catalog.remove_product("CodeToAGI Hoodie")
    print(f"   Removed: {removed.name if removed else 'not found'}")

    print(f"\n💰 Final inventory value: ${catalog.total_inventory_value():,.2f}")

    # --- frozen Category is hashable → use as dict key ---
    print("\n📊 Category index (frozen → hashable):")
    category_map: dict[Category, List[str]] = {}
    for p in catalog.products:
        category_map.setdefault(p.category, []).append(p.name)
    for cat, names in category_map.items():
        print(f"   {cat}: {', '.join(names)}")

    # --- Validation test ---
    print("\n🛡  Validation tests:")
    try:
        bad = Product("Bad Item", price=-10.0, quantity=5, category=electronics)
    except ValueError as e:
        print(f"   ✓ Caught: {e}")

    try:
        bad2 = Product("Bad Item 2", price=10.0, quantity=-1, category=electronics)
    except ValueError as e:
        print(f"   ✓ Caught: {e}")

    print("\n✅ All done — run: mypy --strict ep22_challenge.py")


if __name__ == "__main__":
    main()
