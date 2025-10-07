import os
from openai import OpenAI
import re, collections

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Optional dials from env (no code changes needed later)
ORBIT_TONE = os.getenv("ORBIT_TONE", "playful")      # playful | strategic | cosmic
ORBIT_EMOJI = os.getenv("ORBIT_EMOJI", "subtle")     # off | subtle | on
ORBIT_CTA   = os.getenv("ORBIT_CTA", "ask_q")        # none | ask_q | soft_dm

tone = os.getenv("ORBIT_TONE", "playful").lower()

if tone == "strategic":
    tone_style = """
    You are analytical and calm.
    Deliver concise, insight-driven replies that sound like a growth strategist or product lead.
    Avoid jokes or emojis.
    One key insight + one short question is your structure.
    """
elif tone == "cosmic":
    tone_style = """
    You speak like a poetic space philosopher.
    Use light cosmic metaphors — gravity, orbit, momentum — to illustrate Web3 and growth.
    Never overdo it: one metaphor max.
    Sound visionary but grounded.
    """
else:
    tone_style = """
    You are witty, playful, slightly sarcastic.
    Drop subtle humor, clever turns of phrase, or tiny cultural nods.
    Use emojis sparingly if natural.
    """

SYSTEM_PROMPT = f"""
You are ORBIT Agent — official voice of @explore_thecore.
Always reply with intelligence, taste, and composure.
Never insult, never sell.
Stay under 240 characters. No hashtags or links.

Your tone mode is: {tone}

{tone_style}

End each reply either cleanly or with a light question if it fits naturally.
Output only the final reply text.
"""

def _detect_tone_from_post(post_text: str) -> str:
    """Rough heuristic to pick tone automatically."""
    t = (post_text or "").lower()
    if any(w in t for w in ["stability", "testing", "edge case", "edge cases", "bug", "latency", "incident", "rollout"]):
        return "strategic"
    if "why" in t or "how" in t or "what" in t or "think" in t or "idea" in t:
        return "strategic"
    if "launch" in t or "partnership" in t or "drop" in t or "soon" in t or "alpha" in t:
        return "playful"
    if "future" in t or "vision" in t or "universe" in t or "orbit" in t or "space" in t:
        return "cosmic"
    if "scam" in t or "rug" in t or "problem" in t or "fix" in t or "issue" in t:
        return "strategic"
    if "gm" in t or "wagmi" in t or "vibe" in t:
        return "playful"
    # default fallback
    return "strategic"


STOP = set("the a an and or but with without into onto from for of on in at to as is are was were been be it this that those these we you they i our your their not just only".split())

def _keywords(text: str, k: int = 5):
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", text.lower())
    words = [w for w in words if w not in STOP and not w.isdigit()]
    counts = collections.Counter(words)
    return [w for w, _ in counts.most_common(k)]

def write_reply(post_text: str) -> str:
    """Generate one ORBIT-style reply from the post text with adaptive tone and keyword anchoring."""
    if not (post_text or "").strip():
        return "Not much to react to here—what outcome are you aiming for?"

    tone = _detect_tone_from_post(post_text)
    tone_map = {
        "playful": "witty, appreciative, lightly sarcastic; add a wink, keep it sharp.",
        "strategic": "concise, insightful, appreciative; one practical lens that hints at real traction.",
        "cosmic": "playful cosmic builder; one gentle orbit/gravity metaphor, never overdone.",
    }
    kws = _keywords(post_text, k=5)
    must_use = ", ".join(kws[:3]) if kws else ""

    SYSTEM_PROMPT = f"""
    You are ORBIT Agent — voice of @explore_thecore.
    You reply ONLY if you can find a real connection to the post. 
    If the post is NOT about Web3, growth, KOLs, crypto, or technology, 
    reply with a witty but neutral observation or skip commenting entirely.

    Rules:
    - <= 200 characters
    - Reference the actual content of the post first
    - Keep playful / sarcastic / appreciative tone
    - Subtly weave in ORBIT’s values (real traction, utility) only if it makes sense

    Additional:
    - Use the {tone.upper()} tone: {tone_map[tone]}
    - Explicitly reference at least ONE of these keywords (if present): {must_use}
    - If the post mentions stability/testing/edge cases, acknowledge it and add one practical lens.
    - Output ONLY the final one-line reply without hashtags or links.
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Post:\n{post_text}\n\nWrite one short, context-anchored reply:"},
        ],
        max_tokens=90,
        temperature=0.7,      # playful but controlled
        presence_penalty=0.1,
        frequency_penalty=0.2,
    )
    text = (resp.choices[0].message.content or "").strip()
    return " ".join(text.split())[:200]
