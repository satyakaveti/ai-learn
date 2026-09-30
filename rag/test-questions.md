Here are 15 questions you can use to test retrieval and answer quality when you run this file through your RAG pipeline — a mix of easy single-fact lookups, cross-section comparisons, and "not in the document" edge cases.

## Questions (for testing your RAG system)

1. Within how many days can most items be returned on Amazon.com?
2. How long does it take for a refund to appear if issued to an Amazon.com Gift Card?
3. What is the return window for Apple Brand products sold in new condition?
4. What is the return window for Amazon Renewed products in "Premium" condition?
5. Name three categories of items that cannot be returned on Amazon.com.
6. What is the Late Fee charged if you miss the "return by date" on Amazon.com?
7. What are the weight/size thresholds that classify an item as "heavy and/or bulky" on Amazon.com?
8. How much does Amazon.com automatically refund for return postage on Global Store returns?
9. On Amazon.in, within how many days of successful pickup are refund requests processed?
10. On Amazon.in, how long does a refund to Amazon Pay Balance typically take?
11. How are refunds handled for Pay on Delivery orders on Amazon.in?
12. What is the maximum return shipping cost refunded for Fulfilled by Amazon and Prime-eligible items on Amazon.in?
13. What happens to an Amazon Pay Later balance if no installment has been paid before a return is made?
14. Compare: what is the refund timeline for a prepaid credit/debit card refund on Amazon.in vs. a credit card refund on Amazon.com?
15. According to this document, can you get a cash refund on Amazon.in? *(tests whether the model avoids hallucinating when the answer is a clear "no")*

---

## Answers

1. **Most items** on Amazon.com can be returned **within 30 days of delivery**, provided they're in original or unused condition (some categories have shorter or longer exception windows).
2. Refunds to an **Amazon.com Gift Card or Gift Card balance** typically take **2–3 hours**.
3. **Apple Brand products** (and Boost Infinite Brand products) sold in new condition have a **15-day** return window.
4. Amazon Renewed products in **"Premium" condition** have a **365-day** return window.
5. Any three of: perishables, products posing health/safety risks if returned, products with shipping restrictions, customized products, redeemable products, Amazon Pharmacy products, pet medication products, certain digital products, or automobiles.
6. The **Late Fee** is **20% of the item price** for the first 30 days after the "return by date," and **100% of the item price** afterward.
7. An item is "heavy and/or bulky" if it: weighs **50 lbs or more**, has a longest side (packed) exceeding **59 inches**, or has a girth exceeding **130 inches** (girth = length + 2 × (width + height)).
8. Amazon automatically refunds **up to $20** for return postage on Global Store returns (more can be requested via Customer Service with proof if costs exceed $20).
9. Amazon.in refund requests are processed **within 13 days of successful pickup**.
10. Refunds to **Amazon Pay Balance** on Amazon.in take **up to 4 hours**.
11. Pay on Delivery order refunds on Amazon.in are processed either via **NEFT to the customer's bank account** or as **Amazon Pay balance**.
12. Up to **Rs. 100** in return shipping costs is refunded for Fulfilled by Amazon and Prime-eligible items (credited to Amazon Pay Balance).
13. If no installment has been paid, Amazon **credits the Amazon Pay Later limit with the total order value** instead of issuing a cash/bank refund.
14. **Amazon.in** (prepaid credit/debit card): **up to 5 working days**. **Amazon.com** (credit card): **3–5 business days**. Both are similar in timeframe, though Amazon.in also distinguishes between Amazon-delivered vs. seller-fulfilled order timing.
15. **No** — the document explicitly states: *"Refunds will not be processed in cash."* (A correct RAG answer should reflect this rather than guessing or hedging.)