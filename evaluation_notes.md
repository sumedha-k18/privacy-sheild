## False Positives
- Image: [picture of a random street in europe at night]
- Detected: person at 60% confidence
- Actual content: no person present
- Fix attempted: raised confidence threshold to 0.7

## Interesting Edge Cases
- Aadhaar card flagged as license plate due to numeric rectangular region similarity
- OCR correctly extracted "Male" from gender field
- Devanagari text produced garbled OCR output
- Conclusion: card gets correctly flagged despite wrong detection category

## NER for name detection

## social security number identification
## mobile number identification