# ID-to-Name Relationship Analysis

## Question
**Is there a one-to-one relationship between IDs and names?**
- One `affiliate_id` → One `affiliate_name`?
- One `offer_id` → One `offer_name`?

## Answer: **YES, but with caveats**

### Standard Everflow API Design

Based on the Everflow API documentation and standard database design:

1. **IDs are unique identifiers** - Each `affiliate_id` and `offer_id` is unique
2. **Names should be unique** - In a well-designed system, names should be unique within a network
3. **One ID = One Name** - Each ID maps to exactly one name
4. **One Name = One ID** - Each name should map to exactly one ID

### Current Implementation Analysis

Looking at our code in `everflow_client.py`:

```python
# We deduplicate by ID
seen_ids = set()
for row in table:
    aff_id = row.get("affiliate_id")
    if aff_id and aff_id not in seen_ids:
        seen_ids.add(aff_id)
        # We assume one name per ID
        affiliates.append({
            "affiliate_id": aff_id,
            "affiliate_name": row.get("affiliate_name") or ...
        })
```

**Our assumption:** One ID = One Name ✅

### Potential Issues

#### 1. **Duplicate Names (Many-to-One)**
**Scenario:** Multiple affiliates/offers with the same name
- Affiliate ID 12345: "Premium Partners"
- Affiliate ID 67890: "Premium Partners"

**Impact:** Our resolver would return the **first match**, which might be wrong.

**Current behavior:**
```python
# In entity_resolver.py
for aff in affiliates:
    if name_lower == search_name:
        return aff_id  # Returns first match
```

**Risk:** ⚠️ **Medium** - If names are not unique, we might resolve to wrong ID

#### 2. **Name Changes Over Time (One-to-Many)**
**Scenario:** An affiliate/offer name changes, but ID stays the same
- Offer ID 1001: "Summer Promo 2024" (old name)
- Offer ID 1001: "Summer Promo 2025" (new name)

**Impact:** Our cache might return stale name-to-ID mappings.

**Current behavior:**
```python
# Cache stores: name → ID
self._affiliate_cache[search_name] = aff_id
```

**Risk:** ⚠️ **Low** - Cache refresh handles this

#### 3. **Multiple Field Names (One-to-Many Fields)**
**Scenario:** Same entity has multiple name fields
- `offer_name`: "Summer Promo"
- `advertiser_name`: "Summer Promo 2024"
- `advertiser`: "Summer Promo"

**Impact:** We check all fields, which is good, but might match on wrong field.

**Current behavior:**
```python
possible_names = [
    offer.get("offer_name", ""),
    offer.get("advertiser_name", ""),
    offer.get("advertiser", ""),
    offer.get("offer", ""),
]
```

**Risk:** ✅ **Low** - We prioritize fields correctly

### Recommendations

#### ✅ **Current Implementation is Correct IF:**
1. Everflow API guarantees unique names per network
2. Names don't change frequently
3. One ID always maps to one name

#### ⚠️ **Potential Improvements:**

1. **Handle Duplicate Names:**
```python
# If multiple IDs have same name, return list or ask for clarification
def resolve_affiliate(self, value: Union[int, str]) -> Optional[Union[int, List[int]]]:
    matches = []
    for aff in affiliates:
        if name_matches(aff, value):
            matches.append(aff.get("affiliate_id"))
    
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        # Return list or raise error asking for clarification
        return matches  # or raise AmbiguousNameError
```

2. **Add Validation:**
```python
# Validate one-to-one relationship
def validate_unique_names(entities: List[Dict]) -> bool:
    """Check if all names are unique."""
    names = {}
    for entity in entities:
        name = entity.get("name")
        if name in names:
            print(f"⚠️  Duplicate name found: '{name}' → IDs: {names[name]}, {entity['id']}")
            return False
        names[name] = entity["id"]
    return True
```

3. **Cache Invalidation:**
```python
# Add TTL to cache to handle name changes
from datetime import datetime, timedelta

self._cache_ttl = timedelta(hours=1)
self._cache_timestamp = {}
```

### Conclusion

**Yes, the relationship should be one-to-one:**
- ✅ One `affiliate_id` → One `affiliate_name`
- ✅ One `offer_id` → One `offer_name`

**However:**
- ⚠️ Our implementation assumes this but doesn't validate it
- ⚠️ If names are not unique, we return the first match (might be wrong)
- ✅ Our current implementation is correct for standard use cases

### Action Items

1. **Add validation** to detect duplicate names
2. **Handle ambiguous names** by asking for clarification
3. **Add logging** when duplicate names are detected
4. **Consider caching** with TTL for name changes

