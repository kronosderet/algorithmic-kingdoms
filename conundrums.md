# Mathematical Conundrums — Algorithmic Kingdoms

> Design tensions that emerge from the math and from system interactions.
> Not bugs — features we need to think carefully about.
> Each conundrum has a **Problem**, **Why it matters**, and **Solution direction** (if any).
> Last updated: 2026-03-14

---

## Harmony & Composition

### 1. The Harmony Paradox: Optimal Is Boring
**Problem:** If sum ≡ 0 (mod 7) is always best, every formation chases the same target. Music that never leaves the tonic is elevator music.
**Why it matters:** Strategic diversity requires multiple viable compositions, not one optimal answer.
**Solution direction:** Each mod-7 residue grants a different *flavor* of bonus, not a linear scale. Sum ≡ 6 (leading tone) is "worst harmony" but could grant volatile power that resolved chords can't access. The player chooses *what color of math* they need, not which number is biggest.

### 2. The Substitution Problem: Death Detunes the Chord
**Problem:** A Soldier (tone 2) dies in a perfect formation (sum ≡ 0). Replacing with a free Archer (tone 3) shifts the sum to ≡ 1. The "same slot, different unit" changes the harmony.
**Why it matters:** Combat attrition is constant. If every death breaks harmony, the system punishes fighting.
**Solution direction:** What matters might be *interval structure* (gaps between tones) not absolute sum — like how C-major and D-major are both "major" despite different roots. Transposition preserves chord quality.

### 3. The Monotone Loophole
**Problem:** Seven Soldiers sum to 14 ≡ 0 (mod 7) — "perfect resolution." But monotone formations shouldn't get maximum harmony.
**Why it matters:** Trivial compositions bypassing the system undermines the entire Heptarchy.
**Solution direction:** Harmony = `resolution_bonus × richness_multiplier`. Richness scales with distinct tone count: 1 type = 0.40, 2 = 0.70, 3 = 0.85, 4 = 0.93, 5 = 0.97, 6 = 0.99, 7 = 1.00. Seven identical soldiers: 1.0 × 0.40 = 0.40 (mediocre). One of each type: 1.0 × 1.0 = 1.0 (perfect). Note: the Sage (tone 7 = 0) increases richness without changing the sum — this is intended. The Sage is a free richness boost because amplification IS its role. It doesn't change what you're playing, it makes the room bigger.

### 4. The Rank Octave vs Richness Conflict
**Problem:** Mixed-rank formations get "octave doubling" bonus (Rank-7 + Rank-1 = deepest harmony). But a single-tone formation of mixed ranks (e.g., 3 Rank-1 + 1 Rank-7 Soldiers) gets octave doubling AND the richness penalty (0.40×). A diverse same-rank formation gets richness bonus (1.0) but no octave doubling.
**Why it matters:** These two bonuses are mutually exclusive in practice. The system creates a false choice: mixed-rank monocultures (richer sound, weaker harmony) or same-rank diversity (max harmony, thin sound). A Soldier-only formation sounds beautiful (octave-rich) or mediocre (richness-penalized) — the math disagrees with the narrative.
**Solution direction:** Octave doubling and richness may need to be *additive* not *competing*. Or octave bonus could be a separate multiplier applied after richness, so diverse mixed-rank formations get both. Needs prototyping.

---

## The Sage (Tone 7 = Zero)

### 5. The Sage's Hidden Composition Penalty
**Problem:** The Sage adds 0 to harmony sum (mathematically free) but counts as a distinct tone for richness (free boost from 0.99 → 1.00 at 6→7 types). However, including a Sage means one formation slot is occupied by a glass cannon that doesn't fight conventionally. Practically, you've weakened your combat formation for a functional benefit (field bridge, amplification) that only matters at v12+.
**Why it matters:** Before v12, the Sage has no shadow field to bridge. Its combat value is pure amplification (1.5× resonance). Is that enough to justify the slot? If not, early-Sage adoption is punished.
**Solution direction:** The Sage's 1.5× amplification should be strong enough standalone. But this needs balancing — if 1.5× is too strong, every formation wants one; if too weak, nobody takes the glass cannon. The Sage should feel like a bet: fragile but transformative. Not required, but rewarded.

### 6. The All-Sage Formation
**Problem:** A formation of 7 Sages sums to 0 (perfect resolution) with richness 0.40 (single type). But in a Hilbert formation, it's "the gate fully open." Is this the most powerful formation in the game or a mediocre one?
**Why it matters:** The math says it's harmonically average (richness-penalized). The narrative says it's the endgame singularity. These can't both be true.
**Solution direction:** The Sage's power doesn't come from harmony — it comes from *field access*. A Hilbert full of Sages has mediocre resonance generation but maximum biharmonic potential. Different axis of power, not competing. This needs to be explicit: Sage formations aren't good at singing. They're good at *listening*.

---

## Economy & Scaling

### 7. The Resonance Quadratic Scaling Spiral
**Problem:** Resonance generation = `base × harmony² × rank_bonus`. Quadratic in harmony means doubling harmony multiplies output by 4×. Rank-7 units add 3× multiplier. Late-game formations with high harmony and Rank-7 leaders generate Resonance exponentially faster than early formations.
**Why it matters:** Early game feels tight (low harmony = low generation). Midgame balanced. Late game becomes a spending race where the player's economy spirals ahead of challenge scaling. Either late-game balance breaks, or reality distortion costs must scale exponentially (turning them into an inaccessible money sink).
**Solution direction:** Consider `harmony^1.5` instead of `harmony²`, or add diminishing returns at high harmony. Alternatively, Resonance *decay* — it evaporates over time if not spent, creating a use-it-or-lose-it pressure that prevents stockpiling. The economy of the impossible should feel urgent, not abundant.

### 8. The Sacrificial Economy Asymmetry
**Problem:** The enemy economy runs on *discrete sacrifice* (kill units, convert HP to hex power). The player economy runs on *continuous harmonic generation* (formations singing). These are fundamentally different growth models: discrete sacrifice is bursty and explosive; continuous harmonics are steady and scalable.
**Why it matters:** If sacrifice scaling matches harmonic generation, enemies spam hexes (unfun). If hex power lags, sacrifice feels useless. Finding a formula that makes both economies feel threatening is a genuine balancing challenge.
**Solution direction:** Sacrifice should be high-burst, high-cooldown. Harmony should be low-passive, always-on. The tension is rhythm: enemies choose *when* to be powerful (sacrifice burst), the player chooses *how to sustain* (formation maintenance). Different time signatures, same piece.

### 9. The Combat-Resonance Death Spiral
**Problem:** Fighting disrupts harmony. Disrupted harmony stops Resonance generation. No Resonance means no reality distortion. Weaker fighting disrupts more...
**Why it matters:** Negative feedback loop that can cascade into unrecoverable states.
**Solution direction:** Post-combat "spring-back" — harmony recovers at a rate proportional to the formation's Elasticity characteristic. Creates natural combat rhythm: engage → harmony breaks → retreat to reform → harmony springs back → re-engage. Like breathing. Like a waveform.

### 10. The Rank-7 Cowardice Incentive
**Problem:** Optimal play for Rank-7 units: park them safely in the back, farm Resonance forever. Rational but boring.
**Why it matters:** The most interesting units becoming static resource generators is anti-fun.
**Solution direction:** Rank-7 units generate MORE Resonance inside active high-tier formations than when idle. Solo idle = 1× Resonance. In a Tier 5 formation = 7×. Cowardice is economically suboptimal. The math literally says: harmony multiplies.

---

## Discovery & Strategy

### 11. The Exponential Discovery Space
**Problem:** With 7 tones and formations up to 12 members, possible compositions explode. Do we handcraft recipes or use generative rules?
**Why it matters:** Too many options paralyzes the player. Too few removes the composition-as-gameplay loop.
**Solution direction:** Fixed recipes for 7 formation types (specific ratio requirements). Plus a generative "Free Chord" — any composition summing to 0 mod 7 with 3+ distinct tones auto-qualifies as a valid formation with procedurally generated geometry. This IS the meta-formation — the shape emerges from the math.

### 12. The Commander Monopoly
**Problem:** Random characteristics + fixed commander rules = player might never roll the commander they need. Frustrating RNG.
**Why it matters:** Player agency in composition is the core loop. Losing it to bad rolls kills motivation.
**Solution direction:** Formation signature is a weighted blend of ALL members' revealed characteristics, not just commander's dominant. Commander has highest weight but isn't sole voice. A high-Precision archer partially counteracts a high-Entropy commander. The formation is a chord of characteristics too.

### 13. Formation Discovery vs Formation Emergence
**Problem:** Players "discover" formations by assembling units and triggering a composition check. Once discovered, the formation is a fixed recipe. But if discovery is random (stumble onto 3S+2A), frustration is high. If it requires knowledge (read menus, datamine), it's recipe lookup, not discovery. Once discovered, geometry is fixed — you can't invent hybrid fractals. The formation is a named, static, known thing.
**Why it matters:** This contradicts the vision of players discovering "lost geometries" and the "Free Chord" generative system. If formations are discoverable recipes, they can't also be infinitely emergent.
**Solution direction:** Two tiers: the 7 named formations are discoverable recipes (structured, balanced, safe). The "Free Chord" is true emergence — any valid composition creates a procedurally generated shape. Named formations are instruments. Free Chords are improvisation. Both valid, different skill levels.

---

## The Tier 7 Problem

### 14. The Tier 7 Impossibility
**Problem:** Tier 7 requires seven simultaneous formations, each with a different dominant tone. At minimum 3 members per formation = 21 units in formations. Need all 7 types alive and correctly placed — including a Sage (glass cannon) and a Gatherer (pulled from economy). Enemy AI specifically targets critical tones.
**Why it matters:** If Tier 7 is unachievable in real gameplay, it's either a beautiful mirage (intended) or a broken promise (design fault).
**Solution direction:** May be achievable only in extended games or sandbox — and that might be correct. Tier 7 is "nobody has achieved this" for a reason. Verify during playtesting: is it *theoretically achievable in a real game* or just a mathematical mirage? If mirage: own it. If achievable: make the payoff legendary.

### 15. The Tier 7 Escalation Trap
**Problem:** To achieve Tier 7, you must keep all 7 formation types alive. Enemy AI (v12) learns this and targets Sages/Healers/Gatherers. The more players push toward Tier 7, the more brutally enemies suppress it.
**Why it matters:** Creates either a permanent skill ceiling (no casual player reaches it) or a design fault (enemy AI makes the goal unreachable regardless of skill). Unlike #14, this isn't about resources — it's about the enemy AI specifically adapting to counter the player's most ambitious configuration.
**Solution direction:** The AI should target Tier 7 components but not *perfectly* counter them. Imperfect information: AI should estimate, not know, the player's composition. Also, achieving Tier 7 even briefly (for a few seconds) should trigger its effect — sustained Tier 7 is the mirage, momentary Tier 7 is the achievable goal.

---

## The Shadow Heptarchy

### 16. The ∅ = 3 Generator Coincidence
**Problem:** ∅ = 3 is "the boundary" between player and shadow fields. But 3 is also the player's GF(7) generator, and 5 (the enemy's generator) is its multiplicative inverse (3 × 5 ≡ 1).
**Why it matters:** Is it meaningful that the player's own generator IS the boundary value? This might reshape how ∅ values are interpreted.
**Solution direction:** Lean into it. The thing that generates your harmony is the same thing that touches chaos. Your generator and the enemy's generator are inverses — multiply them and you get 1, the identity, the root note. The boundary isn't between you and the enemy. It's inside you. (Needs more thought — see also Gödel angle: the 7th characteristic is about what cannot be known from within the system, and what cannot be known might be *which generator you are*.)

### 17. The Isomorphism Problem: Are the Sides Actually Different?
**Problem:** Both generators (3 and 5) produce equally valid, equally structured complete cycles of GF(7)*. The design says "the enemy is not evil, the enemy is the same thing heard differently." If that's mathematically true, there's no objective difference between Resonance and Dissonance — only a labeling convention.
**Why it matters:** This is philosophically profound but strategically confusing. Are player and enemy enemies, or harmonically incompatible mirrors? The game wants both, creating thematic tension that may confuse endgame narrative. Players fighting "chaos" discover it's equally valid "order" — does that undermine the entire war?
**Solution direction:** The war is real because the two tunings are *locally incompatible* even though *globally isomorphic*. Like matter and antimatter: same structure, annihilate on contact. The Mandelbrot boundary IS the annihilation zone. The game's truth isn't that fighting is pointless — it's that coexistence requires a bridge (the Sage), not a wall. The war ends not with victory but with translation.

### 18. The Capturable Formation Paradox
**Problem:** When an enemy ritual circle captures a player formation (v12), it remains player-controlled but generates Dissonance. Why does a corrupted formation still follow orders? If corrupted formations defect, the mechanic becomes uncontrollable chaos. If they remain obedient, "corruption" is purely cosmetic.
**Why it matters:** The mechanic needs gameplay consequences that don't trivialize the system (player ignores it) or break control (player can't manage it).
**Solution direction:** Corruption is *functional, not behavioral*. The formation still obeys commands but its passive effects invert: resonance aura becomes Dissonance aura (hurts nearby friendly formations), heal pulse damages, etc. The player retains control but must *quarantine* the corrupted formation away from allies. This creates a spatial puzzle: keep the corrupted formation in enemy territory (where its inverted effects hurt enemies — double inversion!) or retreat and dissolve.

### 19. The Biharmonic Feedback Loop
**Problem:** A ∅ = 3 commander achieving biharmonic resonance generates both Resonance AND Dissonance simultaneously. This creates a positive feedback loop: more resources → sustain longer → generate more → until transcendence or catastrophe.
**Why it matters:** If unchecked, biharmonic resonance = runaway victory. If heavily damped, it's not special enough to reward the extreme difficulty of achieving it. Player agency in the outcome (transcendence vs catastrophe) is unclear.
**Solution direction:** Biharmonic resonance should be *inherently unstable* — it requires active player management (adjusting composition, repositioning) to sustain. Left alone it destabilizes and tears the formation apart. Mastery means riding the edge. The difficulty IS the reward.

### 20. The Mandelbrot Boundary: Place or Process?
**Problem:** At Layers 0-6, the Mandelbrot boundary is a dynamic battle line — player harmony pushes in, enemy chaos pushes back, the frontier shifts. At Layer 7, the same boundary becomes a physical tree trunk where two Trees interlock. Is the boundary a fixed location (the trunk) or a dynamic frontier (the battle line)?
**Why it matters:** If fixed, how do Layer 0-6 players "fight" along something they haven't discovered? If dynamic, how does it become a physical tree trunk? The cosmology conflates the mathematical Mandelbrot set (abstract boundary) with physical geography (trunk of a literal tree). Works poetically. Mechanically unclear.
**Solution direction:** Revelation, not transformation. The boundary was always the trunk — players just couldn't see it until Layer 7. At Layers 0-6, the battle line IS the trunk's projection onto the surface. The Tree's fractal branching was the terrain generation seed all along (Layer 6 already reveals this). Layer 7 just shows what was always underneath.

---

## Audio & Perception

### 21. The Beauty-Horror Paradox
**Problem:** A Tier 6 formation sounds consonant, beautiful, perfect — gorgeous waveform patterns, resolved harmony. Mechanically, it's casting reality distortion that slows enemy time, warps space, and oscillates enemy HP. To the player: triumphant. To the enemy: existential violation.
**Why it matters:** The "beautiful formations = harmonious" metaphor breaks at high tiers. A Tier 6 formation is mathematically harmonic and cosmically monstrous. Is this beautiful math or cosmic horror?
**Solution direction:** This might not need solving. It IS the game's theme. The paradox that mathematics is simultaneously the most beautiful and most terrifying thing humans have discovered. Harmony that warps reality is *supposed* to be unsettling. The player should feel powerful AND uncomfortable. If the audio design achieves both, this is a feature, not a bug.

### 22. The Anti-Formation Definition Gap
**Problem:** The Shadow Heptarchy table lists "Seven Anti-Formations (divergent fractals — Julia sets, strange attractors)" but doesn't specify the mapping. If the shadow field uses the same seven mathematical verbs (Rotation, Growth, Recursion, Iteration, Superposition, Aperiodicity, Limit), what do their anti-formations look like? Julia sets as shadow-Hilbert makes sense. But what's shadow-Rose? Shadow-Koch?
**Why it matters:** When we implement enemy formations, we need actual geometry. Vague "strange attractors" won't produce slot positions.
**Solution direction:** Each anti-formation should be the *divergent dual* of its player counterpart. Rose (rotation) → Lorenz attractor (chaotic rotation). Spiral (growth) → inverse spiral (collapse inward). Sierpinski (recursion) → Cantor dust (recursive deletion). Koch (iteration) → dragon curve (iterative folding). Lissajous (superposition) → Rössler attractor (chaotic interference). Penrose (aperiodicity) → random tiling (true disorder). Hilbert (limit) → Julia set (the limit's shadow, where the iteration diverges). Needs the seven-verbs framework applied to divergent mathematics. The verbs are the same — the *convergence* is what differs.

---

## File Reference

This document extracted from and expands the "Problems Ahead" section of `GDD_Roadmap.md`.
New conundrums should be added here, not in the roadmap.
