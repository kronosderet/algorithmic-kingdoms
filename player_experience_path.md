# Player Experience Path — Algorithmic Kingdoms

> What the player **feels**, **learns**, and **does** — minute by minute.
> Written from the inside out: not "what systems exist" but "what is it like to play this."
> Last updated: 2026-03-14

---

## How to Read This Document

Each phase has:
- **The Player's Mindset** — what they're thinking and feeling
- **Systems Active** — what's mechanically available
- **Learning Moments** — what they discover (ideally by doing, not reading)
- **Risk: Overwhelm** — where we might lose them
- **Risk: Boredom** — where we might bore them
- **Fun Budget** — what makes this phase *worth playing*

---

## Phase 0: The Menu (before the game starts)

**Duration:** 10–30 seconds

**The Player's Mindset:** "What is this?" Algorithmic art background is unusual — no sprites, no portraits. Either intrigued or confused. Difficulty selection: Easy / Medium / Hard.

**Learning Moments:**
- The game looks *different*. Math-generated visuals set expectations: this isn't a standard RTS.
- Three difficulties with no explanation of what they mean.

**Risk: Overwhelm** — None. It's a menu.
**Risk: Boredom** — None, if the algorithmic art is visually compelling.

**Fun Budget:** The art IS the hook. First impression: "This looks like nothing I've played before."

**Design Note:** The menu is the promise. If the Mandelbrot background is beautiful, the player trusts that the game will be beautiful. If it looks like a math homework, they close the window.

---

## Phase 1: The Quiet — "What Do I Do?" (Minute 0–3)

**Duration:** ~3 minutes

**The Player's Mindset:** Dropped into the world. Town Hall at center, 3-4 workers standing idle. No tutorial, no arrows, no "click here" prompts. The map is procedurally generated and unfamiliar. "Where am I? What do I click?"

**Systems Active:**
- Worker selection and movement (click, right-click)
- Resource gathering (right-click resource tiles)
- Camera pan and zoom
- Top bar: 5 resource counters, population, incident counter "0/12"
- Minimap

**Learning Moments:**
1. "I can click things" — selecting workers
2. "Right-click moves them" — RTS muscle memory kicks in (or doesn't)
3. "Those trees/gold deposits are resources" — workers auto-gather on right-click
4. "Numbers go up" — first resource tick is satisfying

**Risk: Overwhelm** — Low. Few elements on screen. But 5 resource types visible from the start is unusual — most RTS games start with 1-2.
**Risk: Boredom** — **Medium.** No enemies, no pressure, no goal communicated. The player is gathering wood and... why? The "0/12" counter means nothing yet. No tension bar movement visible.

**Fun Budget:** Discovery of the world. The procedural map is new every time. Workers moving, gathering, returning — the RTS heartbeat begins. But this phase lives or dies on whether the player *trusts* something interesting is coming.

**Design Questions:**
- [ ] Should the first 3 minutes have ANY environmental storytelling? A ruin? A strange tile? Something that says "there's more here"?
- [ ] Five resource types from minute 0 — is that 3 too many for a first impression? Gold and Wood are intuitive. Iron, Steel, Stone are noise until buildings need them.
- [ ] "0/12" with no label — does the player know this means "survive 12 attacks"?

---

## Phase 2: Building Up — "Okay, I Think I Get It" (Minute 3–5)

**Duration:** ~2 minutes

**The Player's Mindset:** Resources accumulating. Player figures out worker commands, tries building. "What can I build?" Selects worker, discovers hotkeys (or clicks building menu). First barracks placed. Watching it construct is mildly satisfying.

**Systems Active:**
- Building placement (select worker → hotkey → click)
- Build queue (worker auto-constructs)
- Barracks unlocks unit training

**Learning Moments:**
1. "I can build things" — barracks is the first discovery
2. "Buildings take time and resources" — economy matters
3. "The barracks lets me train soldiers" — W key or click
4. First soldier appears — visually distinct from workers

**Risk: Overwhelm** — Low. One building, two unit types. Classic RTS pacing.
**Risk: Boredom** — **Low-Medium.** Building and training is satisfying. But still no threat. Player has been playing for 4-5 minutes with zero danger.

**Fun Budget:** The base grows. Player is creating something. Each new building / unit feels like progress. The worker-to-military pipeline is the oldest RTS satisfaction loop and it works.

**Design Questions:**
- [ ] How does the player discover building hotkeys? Hover tooltips exist (0.6s delay) — is that enough?
- [ ] Training a soldier takes 8 seconds. First archer takes 11 seconds + costs wood. Is the wait appropriate here or does it feel slow when nothing threatens you?

---

## Phase 3: First Blood — "OH. That's What the Counter Is For." (Minute 5)

**Duration:** 30 seconds of warning, 15-30 seconds of combat

**The Player's Mindset:** CALM → FOREBODING → IMMINENT. The narrative bar changes. Screen text appears. "Scouts spotted on the horizon..." Then orange shake: "BRACE YOURSELVES." Enemies appear from the map edge. **This is the pivot moment.** Adrenaline. Panic. Frantic clicking.

**Systems Active:**
- Combat (attack-move, target selection)
- Enemy AI (scouts — flee after 3 seconds of contact)
- Kill bounty (gold per kill)
- Aftermath phase (bonus resources)
- Incident counter: 0 → 1

**Learning Moments:**
1. "The game is about survival" — the counter NOW makes sense
2. "My soldiers fight automatically when enemies get close" — or do they? (Is there auto-aggro?)
3. "Enemies come from the edges" — spatial awareness of the map matters
4. "I got gold for killing them" — violence is economically rewarded
5. "The bar that says '1/12' means I need to survive 12 of these" — the goal crystallizes

**Risk: Overwhelm** — **Medium.** First combat with no tutorial. If the player hasn't trained soldiers, they might lose workers. If they have 2 soldiers, the scouts are trivial. The variance between "prepared" and "caught off guard" is high.
**Risk: Boredom** — None. First combat is always engaging.

**Fun Budget:** **This is the game's first real fun.** The tension ramp (calm → foreboding → combat → relief) is a complete emotional arc in 60 seconds. The aftermath bonus feels like a reward. The counter clicking from 0 to 1 creates the first dopamine of progress.

**Critical Design Insight:** Everything before this moment is setup. If this moment doesn't land — if the player dies, or if it's too easy and anticlimactic, or if they don't understand what happened — the game loses them. **The first incident is the game's audition.**

**Design Questions:**
- [ ] First wave is always scouts (flee on contact). Is "enemies that run away" a satisfying first combat? Player might feel cheated: "I didn't really win, they just left."
- [ ] If the player has NO military units at minute 5 (spent all resources on economy), what happens? Workers can't fight. Is that a soft-fail or a hard-fail? Should workers have minimal attack?
- [ ] The foreboding → imminent → active transition is the game's signature. Does the audio/visual sell it?

---

## Phase 4: The Economy Loop — "More Workers, More Soldiers, More Buildings" (Minute 5–15)

**Duration:** ~10 minutes

**The Player's Mindset:** Post-combat high. "I need to be ready for the next one." Economy enters the classic RTS macro loop: train workers, train soldiers, build towers, gather more. The player is now *playing the game* — they understand the core loop.

**Systems Active:**
- Everything from phases 0-3
- Tower construction (ranged defense, cannonballs)
- Refinery (iron → steel conversion)
- Multiple unit types training simultaneously
- Cooldown between incidents (90-180s)
- Tension meter slowly climbing

**Learning Moments:**
1. "Towers shoot automatically" — passive defense is possible
2. "Iron needs a Refinery to become Steel" — resource chains emerge
3. "The tension bar is creeping up" — something's coming again
4. "I should probably have more soldiers before the next attack" — planning ahead
5. "My soldier got a rank-up!" (Rank 0 → 1) — first veteran, XP visible

**Risk: Overwhelm** — **Low-Medium.** The economy is straightforward. But if the player hasn't discovered towers or the refinery, they may feel underprepared.
**Risk: Boredom** — **Medium in the lulls.** 90-180 second cooldowns between incidents can feel long. The player is waiting. Macro is active (training, building) but not exciting. This is where a "fast forward" urge would hit.

**Fun Budget:** Base building is evergreen. Each new building type is a small discovery. The tension meter rising creates anticipation. Second and third incidents are slightly harder — the ramp is gentle but present.

**Design Questions:**
- [ ] Cooldown between incidents: 90-180s. On Easy, that's up to 3 minutes of nothing happening. Is the economy engaging enough to fill that time?
- [ ] The Rank 0 → 1 promotion: is it visible enough? Celebrated enough? This is a KEY moment (unlocks squads later).
- [ ] Player has 5 resources, 3 building types, 3 unit types by minute 15. That's manageable. But are all 5 resources pulling their weight narratively, or do some feel like filler?

---

## Phase 5: The Squad Unlock — "Wait, They Can Do WHAT?" (Minute 12–20)

**Duration:** Discovery moment + 5 minutes of experimentation

**The Player's Mindset:** A unit hits Rank 1. The squad bar appears or activates. "No squads" message hints at something new. Player experiments: selects multiple Rank 1+ units, discovers squad formation. Suddenly their blob of soldiers snaps into a geometric pattern. **This is the game's second major "oh" moment.**

**Systems Active:**
- Squad formation (select units → form squad)
- Formation selection (F1-F4: Rose, Spiral, Sierpinski, Koch)
- Stance selection (F5-F8: Aggressive, Defensive, Guard, Hunt)
- Squad selection (number keys 1-9)
- Formation geometry visible on-screen

**Learning Moments:**
1. "Units can form squads" — the game has a layer I didn't see before
2. "Squads have shapes" — fractal geometry appears for the first time
3. "The shape affects how they fight" — Polar Rose vs Koch feel different
4. "F5-F8 changes their behavior" — stances add tactical control
5. "The geometry is... math?" — first hint that formations are algorithmically generated

**Risk: Overwhelm** — **HIGH.** This is the danger zone. In the span of 2 minutes, the player gains access to: squad creation, 4 formations, 4 stances, squad selection hotkeys, formation geometry, and (soon) the discovery system. That's 6+ new systems at once. The UI adds the squad bar, formation buttons, stance buttons. Information density spikes.
**Risk: Boredom** — None. This is inherently interesting. But if the player can't figure out HOW to form squads, frustration replaces curiosity.

**Fun Budget:** **This is the game's identity reveal.** The first time units snap into a Polar Rose pattern, the player either grins or furrows their brow. This moment must feel like "oh, THIS is the game." The fractal geometry is the visual hook that the menu promised.

**Critical Design Insight:** The gap between "I have Rank 1 units" and "I have a functioning squad in formation" is the game's steepest learning cliff. Every system unlocks at once. The player needs to:
1. Know they CAN form squads (how?)
2. Select the right units (only Rank 1+)
3. Form the squad (what button? what UI?)
4. Choose a formation (F1-F4 — but which one? why?)
5. Choose a stance (F5-F8 — but what do they mean?)

**Design Questions:**
- [ ] **This is where the playtest will be most revealing.** Does your wife find the squad unlock intuitive or baffling?
- [ ] Should formations unlock one at a time (Rose first, then Sierpinski after the next incident, etc.) instead of all at once?
- [ ] Is there a visual/audio cue that says "hey, you can form squads now"? The notification system exists — is the message clear enough?
- [ ] The jump from "click units, right-click to attack" to "form squads with formations and stances" is a genre shift from casual RTS to tactical RTS. Is the player ready?

---

## Phase 6: The Rhythm — "I Know the Dance Now" (Minute 20–40)

**Duration:** ~20 minutes

**The Player's Mindset:** The core loop is internalized: gather → build → form squads → fight → recover → repeat. Each incident is slightly harder. The player is making real tactical decisions: which formation for which situation, where to position squads, when to use towers vs mobile defense. **This is where the game should be the most consistently fun.**

**Systems Active:**
- All previous systems
- Multiple squads (2-4)
- Enemy composition variety (soldiers, archers, sappers, raiders)
- Multi-directional attacks
- Morale system (enemies flee when outnumbered)
- Adaptive difficulty (enemy AI counter-picks player composition)

**Learning Moments:**
1. "Sappers go for my buildings!" — economy raiding creates urgency
2. "Enemies attack from two sides now" — map awareness matters
3. "My Koch formation holds a chokepoint better" — formation choice is tactical
4. "If I kill enough, they flee" — morale is exploitable
5. "The enemy sent archers because I had towers" — AI adapts (if the player notices)

**Risk: Overwhelm** — **Low.** Systems are already learned. New enemy types introduce complexity gradually. Each new enemy type is a "puzzle" — what counters sappers? What handles raiders?
**Risk: Boredom** — **Low-Medium.** The rhythm is established. Risk of repetition if incidents feel samey. Enemy variety is the antidote.

**Fun Budget:** Peak gameplay. The player feels competent. Each incident is a test they're equipped to handle but not guaranteed to pass. Squad micro feels rewarding. Economy macro feels productive. The tension curve creates natural pacing.

**Design Questions:**
- [ ] Is 20 minutes of "the rhythm" the right length, or does it need a mid-game event to break the pattern? (A boss? A special incident? A story beat?)
- [ ] Counter-pick AI: does the player NOTICE the AI adapting? If not, it's wasted design. If yes, it feels brilliant.
- [ ] Resonance generation from formations: is this visible? Does the player understand they're generating a resource by having good formations? Or is it invisible background math?

---

## Phase 7: The Escalation — "This Is Getting Serious" (Minute 40–60)

**Duration:** ~20 minutes

**The Player's Mindset:** Incidents are harder. Multi-directional attacks. Siege units. Warlocks with dissonance effects. The tension meter is amber/orange. "I might actually lose this." Every incident requires real response. No more autopilot.

**Systems Active:**
- All previous
- Strong/deadly incident tiers
- Dissonance effects on enemies
- 3-directional attacks
- Siege compositions (shieldbearers + healers + damage)

**Learning Moments:**
1. "I can't just have one death-ball squad" — need to split forces
2. "Shieldbearers protect the archers behind them" — enemy compositions have synergy
3. "Healers need to die first" — target priority matters
4. "My base is being hit from three sides" — strategic positioning of squads

**Risk: Overwhelm** — **Medium.** Simultaneous multi-front combat requires fast decision-making. Players who haven't mastered squad controls may feel the game's input complexity outpaces their ability.
**Risk: Boredom** — **None.** If the player is still playing at minute 40, they're engaged. The escalation provides natural pressure.

**Fun Budget:** The game tests everything the player has learned. Winning an escalated incident feels earned. Losing one creates "what should I have done differently?" — the mark of good difficulty design.

---

## Phase 8: The Finale — "Everything I've Got" (Minute 60–90)

**Duration:** 20-30 minutes (or less if the player loses)

**The Player's Mindset:** Tension meter is red. Incidents are deadly. The counter is 10/12 or 19/22. "I just need to survive a few more." Every unit matters. Every death hurts. The player is leaning forward.

**Systems Active:** Everything. Maximum complexity. Maximum stakes.

**Learning Moments:** None new. This is the exam, not the lesson.

**Risk: Overwhelm** — **High for unprepared players.** 30+ enemies from 3 directions. If the player hasn't developed multi-squad tactics, this is a wall.
**Risk: Boredom** — None.

**Fun Budget:** **This is the payoff.** The moment the counter hits 12/12 and the victory screen appears, the player has earned it. Every system, every formation, every tactical decision led here. The game should make this feel like a triumph.

**Design Questions:**
- [ ] Is the victory screen satisfying? What stats does it show? Does it acknowledge the player's journey?
- [ ] If the player dies at 11/12, is that devastating or motivating? (Both is correct.)
- [ ] On Easy, this takes ~75 minutes. On Hard, potentially 90+. Is that too long for a single session? Should there be save/load?

---

## The Roadmap Phases (v11–v13): How They Change the Path

### v11 — The Heptarchy (7 unit types, 7 characteristics, harmonic math)

**Impact on Experience Path:**
- Phase 1-2: Now 7 resource types? 7 unit types? The "quiet" phase has more to absorb.
- Phase 5: Formation discovery becomes composition math (tone ratios, harmony sums). The squad unlock moment is now a *math puzzle*.
- Phase 6+: Harmony quality, resonance multipliers, and characteristic discovery add continuous optimization layers.

**Overwhelm Risk:** **Very high** without careful onboarding. Seven of everything is the design's philosophy — but it's also seven times the learning surface.

**Mitigation Ideas:**
- Only show 3 resources initially (Gold, Wood, Iron). Reveal others as buildings require them.
- Start with 3 unit types available. Unlock others through gameplay progression.
- Harmony % displayed simply: a color bar from red → gold. No numbers until the player asks.
- Characteristics revealed ONE AT A TIME per unit, not dumped as a stat sheet.

### v12 — Blood Magic & The Sage (enemy hex economy, 7th unit type, shadow field hints)

**Impact on Experience Path:**
- Phase 3+: Enemy hexes add a reactive layer — "that hex made my soldiers miss!" The combat vocabulary expands.
- Phase 5+: The Sage as a unit choice is a bet: fragile, powerful, different. First time a unit feels like a *strategic commitment* rather than "more is better."
- Phase 7-8: Capture/corruption mechanics turn late-game into chess. Corrupted formations must be quarantined. Subsumption turns enemy power against them.

**Overwhelm Risk:** Medium. Hexes are reactive (player responds to them), not proactive (player doesn't need to cast them). The Sage is optional. Capture is late-game.

### v13 — The Mirror Field (Shadow Heptarchy, Layer 7, biharmonic resonance)

**Impact on Experience Path:**
- Entirely new endgame layer for experienced players.
- The revelation that the enemy has a complete mirror system is a *narrative* moment, not a complexity moment — if done right.
- ∅ values and biharmonic resonance are for the 1% of players who want to go deep.

**Overwhelm Risk:** Low if gated behind late-game discovery. High if explained up front.

---

## Known Pain Points (To Test)

These are the moments most likely to make a new player quit. The playtest should focus here.

### 1. "I Don't Know What to Do" (Minute 0-2)
No tutorial. No objective shown. Player stares at workers. **Test:** Does the player start gathering within 60 seconds? If not, what are they trying to click?

### 2. "What Are All These Resources?" (Minute 0-5)
Five resource types from the start. Gold and Wood are obvious. Iron, Steel, Stone are noise. **Test:** Does the player check all 5 counters? Do they understand the difference? Or do they ignore 3 of them?

### 3. "I Died and I Don't Know Why" (Minute 5)
First incident with no military. Workers die. Game might end. **Test:** Did the player build a barracks before minute 5? If not, do they understand they lost because they had no army?

### 4. "How Do I Make Squads?" (Minute 12-20)
The squad unlock cliff. **Test:** How long from "first Rank 1 unit" to "first functioning squad"? What buttons does the player try? Where do they get stuck?

### 5. "Which Formation? Why?" (Minute 15-25)
Four formations unlocked. No clear guidance on when to use which. **Test:** Does the player try all 4? Do they notice a difference? Do they settle on one and ignore the rest?

### 6. "The Lulls Are Too Long" (Throughout)
90-180 second cooldowns. **Test:** Does the player alt-tab during cooldowns? Look at their phone? Or are they actively macro-ing?

### 7. "I Lost at 11/12" (Finale)
Devastating late loss. **Test:** Does the player immediately restart? Or close the game? The answer tells us if the difficulty curve is right.

---

## Playtest Protocol (For First-Time Tester)

### Setup
- Easy difficulty
- No prior explanation of the game
- Screen recording if possible (mouse position reveals confusion)
- Player thinks aloud: "I'm going to click this because..."

### Observe (Don't Help)
- **Minute 0-2:** What do they click first? How long until they select a worker?
- **Minute 2-4:** Do they discover building? How?
- **Minute 4-5:** Do they have military units before first incident?
- **Minute 5:** Reaction to first combat. Panic? Calm? Confusion?
- **Minute 12-20:** Squad unlock. How do they figure it out? Do they?
- **Minute 20-40:** Are they having fun? Are they bored? Are they overwhelmed?
- **General:** What questions do they ask? (Each question = a missing signal in the UI)

### After the Session
- "What was confusing?"
- "When did you feel most in control?"
- "When did you feel most overwhelmed?"
- "When were you bored?"
- "Would you play again? Why / why not?"
- "What did you think the game was about?"

---

## File Reference

- `GDD_Current_v9.md` — Implemented systems spec
- `GDD_Roadmap.md` — Version pipeline and future design
- `conundrums.md` — Mathematical design tensions
- `constants.py` — Game constants (timing, costs, scaling)
- `gui.py` — UI layout and information display
- `enemy_ai.py` — Wave composition and difficulty ramp
