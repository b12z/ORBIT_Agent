import random

TONE_BANK = {
    "sarcastic": [
        "Vanity metrics called; they want their dignity back.",
        "Maybe engagement farming is the new cardio?",
        "Imagine if numbers translated to real traction. Wild thought.",
    ],
    "curious": [
        "Ever wonder what happens when growth actually means results?",
        "If traction had a smell, would it still be dopamine?",
        "Curious how many of these followers even blink at the product.",
    ],
    "teasing": [
        "Some chase clout. Others chase outcomes. Guess which camp we’re in.",
        "Growth theatre is fun until the curtain drops.",
        "Keep the hype; we’ll keep the retention curve.",
    ],
    "engaging": [
        "We’ve been there. Tried the grind. Found a smarter orbit.",
        "Real talk—what metric actually matters to you lately?",
        "Let’s just say the algorithm’s about to meet accountability.",
    ],
}

def generate_reply(post_text: str) -> str:
    """Return a one-line ORBIT-style response."""
    tone = random.choice(list(TONE_BANK.keys()))
    return random.choice(TONE_BANK[tone])