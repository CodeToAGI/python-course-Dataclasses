# CodeToAGI — Episode 22 Challenge Solution
## Python Dataclasses: Build a Product Catalog

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![mypy](https://img.shields.io/badge/mypy--strict-0%20errors-brightgreen)
![Series](https://img.shields.io/badge/CodeToAGI-Episode%2022-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> **Full solution to the Episode 22 challenge from the [CodeToAGI YouTube series](https://youtube.com/@CodeToAGI).**  
> Topic: `@dataclass` · `field()` · `__post_init__` · `frozen=True` · `order=True` · `slots=True`

---

## 📺 Watch the Episode

**[Python Dataclasses: Stop Writing \_\_init\_\_ Forever | @dataclass, frozen, slots | Ep 22](https://youtube.com/@CodeToAGI)**

---

## 🎯 Challenge Requirements

The challenge from the video has 5 steps:

| Step | Requirement |
|------|-------------|
| 1 | `Category` dataclass with `frozen=True` — fields: `name: str`, `description: str` |
| 2 | `Product` dataclass with `name`, `price: float`, `quantity: int`, `category: Category`, `tags: List[str]` |
| 3 | `__post_init__` — validate `price >= 0` and `quantity >= 0` |
| 4 | `Catalog` dataclass with `add_product`, `remove_product`, `search_by_category` methods |
| 5 | `mypy --strict ep22_challenge.py` → **0 errors** |

---

## 📁 File Structure

```
ep22-challenge/
├── ep22_challenge.py   ← complete solution (run this)
└── README.md           ← this file
```

---

## 🚀 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/codetoagi-ep22.git
cd codetoagi-ep22
```

### 2. Install dependencies
```bash
pip install mypy
```
> No other packages needed — only Python standard library.

### 3. Run the solution
```bash
python ep22_challenge.py
```

### 4. Run mypy strict check
```bash
mypy --strict ep22_challenge.py
```
Expected output:
```
Success: no issues found in 1 source file
```

---

## 🧱 What's Inside

### `Category` — frozen + slots
```python
@dataclass(frozen=True, slots=True)
class Category:
    name: str
    description: str = ""
```
- `frozen=True` → instances are immutable (no reassignment after creation)
- `slots=True` → ~40% less memory (Python 3.10+)
- Hashable by default → safe to use as **dict keys** and **set members**

---

### `Product` — validated + derived field
```python
@dataclass(order=True)
class Product:
    name: str
    price: float
    quantity: int
    category: Category
    tags: List[str] = field(default_factory=list)
    description: str = ""
    total_value: float = field(default=0.0, init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError(...)
        if self.quantity < 0:
            raise ValueError(...)
        self.total_value = round(self.price * self.quantity, 2)
```

Key concepts used:

| Feature | Where |
|---------|-------|
| `field(default_factory=list)` | `tags` — safe mutable default |
| `field(init=False)` | `total_value` — not in constructor |
| `field(compare=False)` | `total_value` — excluded from `==` |
| `__post_init__` | validation + computed field |
| `order=True` | enables `<`, `<=`, `>`, `>=`, `sorted()` |

Extra methods:
- `restock(amount)` — add stock and recompute `total_value`
- `apply_discount(percent)` — reduce price and recompute `total_value`

---

### `Catalog` — search + aggregate
```python
@dataclass
class Catalog:
    name: str
    products: List[Product] = field(default_factory=list)
```

Methods:

| Method | Description |
|--------|-------------|
| `add_product(product)` | Add with duplicate name guard |
| `remove_product(name)` | Remove by name, returns `Optional[Product]` |
| `search_by_category(category)` | Filter by `Category` instance |
| `search_by_tag(tag)` | Case-insensitive tag filter |
| `search_by_name(query)` | Partial name search |
| `in_stock()` | Products with `quantity > 0` |
| `out_of_stock()` | Products with `quantity == 0` |
| `sorted_by_price(descending)` | Price-sorted list |
| `sorted_by_name()` | Alphabetical list |
| `total_inventory_value()` | Sum of all `total_value` |
| `most_valuable()` | Highest `total_value` product |
| `cheapest()` | Lowest price product |
| `summary()` | Formatted overview string |

---

## 📊 Sample Output

```
╔══ CodeToAGI Store (5 products) ══
║  Total inventory value : $14,696.30
║  In stock              : 4
║  Out of stock          : 1
╠══ Products:
║  [✓] Clean Code | $39.99 x 0 units = $0.00 | [Books]
║  [✓] Laptop Pro 15 | $1,299.99 x 10 units = $12,999.90 | [Electronics]
║  [✓] Python Crash Course | $34.99 x 200 units = $6,998.00 | [Books]
║  [✓] Wireless Headphones | $89.99 x 50 units = $4,499.50 | [Electronics]
║  [✓] CodeToAGI Hoodie | $49.99 x 30 units = $1,499.70 | [Clothing]
╚══════════════════════════════════════════════════════
```

---

## ✅ mypy --strict Output

```
Success: no issues found in 1 source file
```

All type annotations are complete. No `Any`, no missing return types, no untyped functions.

---

## 💡 Key Concepts Covered

| Concept | Explanation |
|---------|-------------|
| `@dataclass` | Auto-generates `__init__`, `__repr__`, `__eq__` |
| `frozen=True` | Makes instances immutable — raises `FrozenInstanceError` on write |
| `slots=True` | Replaces `__dict__` with fixed array — less memory, faster access |
| `order=True` | Generates `__lt__`, `__le__`, `__gt__`, `__ge__` for comparison |
| `field(default_factory=list)` | Safe mutable default — new list per instance |
| `field(init=False)` | Field not exposed in constructor — set in `__post_init__` |
| `field(compare=False)` | Excluded from `__eq__` and ordering |
| `__post_init__` | Runs right after generated `__init__` — validation + derived fields |
| `Optional[T]` | Return type for methods that may return `None` |
| Type aliases | `List[Product]`, `List[str]`, `dict[Category, List[str]]` |

---

## 🗺️ CodeToAGI Series Roadmap

| Episode | Topic | Link |
|---------|-------|------|
| EP 20 | Testing with pytest | [Watch](#) |
| EP 21 | Type Hints & mypy | [Watch](#) |
| **EP 22** | **Dataclasses** ← you are here | [Watch](#) |
| EP 23 | Abstract Base Classes & Protocol | Coming soon |
| EP 24 | Decorators Deep Dive | Coming soon |

---

## 🙌 Contributing

Found a cleaner way to write any part of the solution?  
Open a PR — all improvements welcome.

---

## 📜 License

MIT — use freely, learn well.

---

## 👤 Author

**Mahaz Abbasi**  
YouTube: [@CodeToAGI](https://youtube.com/@CodeToAGI)  
*Python to Agentic AI — completely free, one episode every day.*
