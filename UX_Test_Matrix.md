# UX Test Matrix — 3×3 User Journey Scenarios

> Run these scenarios after every major content update to validate the UX before tuning.
> Each scenario is a simulated playthrough from the perspective of a specific player archetype at a specific difficulty.
> Score each checkpoint 1-5: (1) confused/stuck, (2) struggling, (3) adequate, (4) smooth, (5) invisible/perfect.
> Created: 2026-03-15

---

## Player Archetypes

| Archetype | Description | Mental Model | What They Notice |
|---|---|---|---|
| **Nova** | First RTS ever. Bought the game because "math art" looked cool. Doesn't know what a hotkey is. Will click everything. Will panic at first enemy wave. | "I click things and stuff happens?" | Missing affordances, unclear buttons, anything that requires knowledge the game didn't teach |
| **Meridian** | 40 hours in. Reached Layer 3. Understands economy → army → survive loop. Discovered 2 formations by accident. Starting to feel the harmony system but can't articulate it. Comfortable on Easy, attempting Medium. | "I know the basics but I feel like there's more I'm not seeing" | Hidden depth that should be surfaced, formation UX friction, harmony feedback gaps, moments where they know WHAT but not WHY |
| **Zenith** | 1500 hours. Has beaten Hard. Knows every hotkey, every counter, every formation trick. Reads the event log CSV for fun. Optimizes build orders. Wants the game to challenge them, not teach them. | "Don't waste my time. Give me control and get out of my way" | Input lag, unnecessary confirmations, information density too low, missing advanced features, anything that slows APM |

---

## The Matrix

```
              EASY          MEDIUM         HARD
Nova       [Scenario 1]  [Scenario 2]  [Scenario 3]
Meridian   [Scenario 4]  [Scenario 5]  [Scenario 6]
Zenith     [Scenario 7]  [Scenario 8]  [Scenario 9]
```

---

## Scenario 1: Nova × Easy

**The first 10 minutes of someone who has never played an RTS.**

> *"I saw the Mandelbrot menu and thought this was an art program. Now there are little shapes moving and I have no idea what's happening."*

### Starting State
- 300g, 150w, 4 workers, Town Hall
- Map: 64×64 (small, manageable)
- First incident at 300s (5 minutes) — generous ramp
- 7 incidents to win

### Journey Checkpoints

| Time | What Happens | What Nova Tries | UX Question | Score |
|---|---|---|---|---|
| **0:00** | Game starts. 4 workers idle near Town Hall. Resources visible in top bar. | Looks at screen. Moves mouse around. Clicks on a worker. | **Does the player understand they need to DO something?** Is there any prompt, tutorial hint, or visual cue that says "click a worker"? Or is it just... a screen? | __ /5 |
| **0:30** | Nova clicked a worker. Bottom panel shows worker info. | Reads the panel. Sees resource icons but doesn't know what they mean. Tries right-clicking on things. | **Does the bottom panel explain itself?** Are the resource icons labeled? Is there a tooltip? Does the player know that right-click = command? | __ /5 |
| **1:00** | Nova right-clicked on a tree (by luck or experimentation). Worker walks over and starts gathering. | "Oh! It went to the tree!" Tries right-clicking other workers on trees. | **Is the gather feedback clear?** Can Nova see wood numbers going up? Is there a floating +10 or similar? Does the worker's animation clearly show "gathering"? | __ /5 |
| **2:00** | 2-3 workers gathering. Nova notices gold/iron on minimap (maybe). Tries clicking the Town Hall. | Sees the Town Hall panel. Sees "Q: Train Worker" button. | **Is training discoverable?** Is the Q hotkey visible on the button? Does the button show the cost? Can Nova tell if they can afford it? Is the training queue visible? | __ /5 |
| **3:00** | Nova has some resources. Wants to build but doesn't know how. | Clicks around the screen. Maybe tries pressing number keys. Maybe right-clicks empty ground. | **Is building placement discoverable?** How does Nova learn that selecting workers + pressing 1-4 places buildings? Is there a build menu? A button? Anything? | __ /5 |
| **4:00** | Nova managed to place a Barracks (or didn't — note which). | If placed: tries to figure out how to train soldiers. If not: still stuck trying to build. | **Is the Barracks → Soldier connection clear?** After clicking the Barracks, is T/E visible as "Train Soldier / Train Archer"? | __ /5 |
| **5:00** | **First incident approaches.** Tension meter starts rising (maybe Nova doesn't notice). Narrative text changes to "Foreboding". | Probably doesn't notice the tension meter. Continues economy. | **Does the tension meter communicate danger?** Does the color change from blue → amber register? Does "Foreboding" mean anything to Nova? Or is the first wave a complete surprise? | __ /5 |
| **5:30** | **INCIDENT 1.** Enemy soldiers spawn from edge. Red dots on minimap. | Panics. Clicks on enemies. Doesn't know how to fight. | **THE PANIC MOMENT.** Can Nova figure out: (a) those are enemies, (b) right-click military units on them to attack, (c) towers auto-fire if built? How much does the game help RIGHT NOW? | __ /5 |
| **6:00** | First combat happening. Workers probably getting killed. Town Hall maybe taking damage. | Frantically clicking. Trying to run workers away. | **Is combat feedback readable?** HP bars visible? Damage numbers? Can Nova tell who's winning? Does the Town Hall garrison mechanic surface itself? | __ /5 |
| **7:00** | Incident 1 resolves (enemies dead or buildings lost). Aftermath state. | Assesses damage. Maybe lost a worker or two. Confusion about what just happened. | **Is the aftermath clear?** Does the game explain "you survived wave 1"? Is the incident counter visible and meaningful? Does Nova know more waves are coming? | __ /5 |
| **10:00** | Should be building army now. Incident 2 approaching. | Training soldiers (if they figured it out). Gathering resources. | **Has the loop clicked?** Gather → Build → Train → Defend. If Nova is doing this, the UX works. If they're still confused about building placement or training, it doesn't. | __ /5 |
| **15:00** | Incident 3-4. Fade Rangers (archers) appear at incident 2. Blight Reapers at incident 3. | Dealing with ranged enemies for the first time. Reapers targeting workers. | **Are enemy abilities communicated?** Does Nova understand that Reapers specifically target economy? That archers outrange soldiers? Is the enemy info panel (click to inspect) discoverable? | __ /5 |
| **25:00** | Mid-game. Should have 2+ barracks, towers, mixed army. Formations discoverable. | Maybe discovered a formation by accident (moving 3+ military together). | **Formation discovery UX.** Did the discovery trigger? Was it explained? Does Nova understand what the formation does? Or did it just happen and they didn't notice? | __ /5 |
| **End** | Victory (7 incidents) or defeat. | Reviews the game-over screen. | **Does the end screen teach?** Does it show what went right/wrong? Is replay accessible? Does Nova want to play again? | __ /5 |

### Nova × Easy: Critical UX Failures to Watch For
- [ ] Nova never discovers how to place buildings (no build menu, only hotkeys)
- [ ] Nova never trains military units (doesn't realize Barracks enables training)
- [ ] Nova's workers die in wave 1 and they can't recover (death spiral, no guidance)
- [ ] Nova never discovers formations (the pending-group mechanic is invisible)
- [ ] Nova doesn't understand the tension meter / incident system at all
- [ ] Nova doesn't know about right-click commands (RTS convention, not universal knowledge)

---

## Scenario 2: Nova × Medium

**A new player who accidentally picked Medium because they "don't play on Easy."**

> *"I've played Civilization, how hard can this be? ...why is everything dead."*

### Starting State
- 200g, 100w, 3 workers
- Map: 128×128 (four times larger — Nova may feel lost)
- First incident at 270s (4.5 min) — tighter
- 14 incidents to win

### Journey Checkpoints

| Time | What Happens | What Nova Tries | UX Question | Score |
|---|---|---|---|---|
| **0:00** | Game starts. Fewer resources than Easy. Larger map. Only 3 workers. | Same confusion as Scenario 1, but with less runway. | **Does the difficulty difference surface itself?** Does Nova know they have less time? Is there any indication that Medium is harder? Or do they only find out when they die? | __ /5 |
| **3:00** | Economy slower (3 workers vs 4). Probably hasn't placed Barracks yet. | Still figuring out building. Only 3 workers means fewer resources. | **Is the economy pace punishing enough to be unfun?** On Easy, 4 workers and more gold buys exploration time. On Medium, the 200g/3W start is tight. Does Nova hit a resource wall before understanding the loop? | __ /5 |
| **4:30** | **Incident 1 imminent.** Tension rising faster (0.005 vs 0.003 drift). | Probably no army. Maybe 1 soldier training. | **The crunch.** Faster tension, fewer resources, bigger map. Nova likely has no defense. Does the game communicate "you're in danger" early enough to matter? | __ /5 |
| **5:00** | Incident 1 hits. Nova has 0-1 soldiers. Enemies stronger than Easy (+5% HP/wave vs +4%). | Town Hall fight. Workers dying. Possible early defeat. | **Is early defeat handled gracefully?** If Nova loses all buildings in incident 1-2, is the game-over screen helpful? Does it suggest trying Easy? Or is it just "Defeat" and back to menu? | __ /5 |
| **8:00** | If survived: scrambling. If not: restarting or quitting. | Struggling to understand what went wrong. | **Is difficulty feedback contextual?** After a defeat, does anything say "Medium starts with fewer resources and faster waves — try Easy to learn the basics"? | __ /5 |
| **15:00** | If still alive: barely keeping up. Incidents 4-6. New enemy types (Raiders at 4, Siege at 6). | Reacting, not planning. Economy insufficient. | **Does Medium feel like a wall or a slope?** The jump from Easy (7 incidents, slow ramp) to Medium (14 incidents, faster ramp) is steep. Does the UX support a player who's over their head? | __ /5 |
| **End** | Likely defeat between incidents 4-8. | Frustration or determination. | **Does the defeat motivate or discourage?** Does Nova learn from the loss? Is there enough feedback to know WHY they lost? | __ /5 |

### Nova × Medium: Critical UX Failures to Watch For
- [ ] Nova doesn't realize Medium is significantly harder (no pre-game warning)
- [ ] First incident kills Nova before they understand the game
- [ ] No suggestion to drop to Easy after early defeat
- [ ] Map size (128×128) causes Nova to lose their base (camera lost, no minimap literacy)
- [ ] Defeat screen is unhelpful — no "what went wrong" feedback

---

## Scenario 3: Nova × Hard

**Pain. This scenario exists to test how gracefully the game handles guaranteed failure.**

> *"I wanted a challenge." (Survives 90 seconds.)*

### Starting State
- 180g, 100w, 3 workers
- Map: 256×256 (massive — Nova will be lost immediately)
- First incident at 240s (4 min)
- 21 incidents to win

### Journey Checkpoints

| Time | What Happens | What Nova Tries | UX Question | Score |
|---|---|---|---|---|
| **0:00** | Huge map. Nova zooms out, sees vast emptiness. Town Hall is a tiny spec. | "Where am I? Where is anything?" | **Does the camera start focused?** On a 256×256 map, is Nova zoomed in on their base or zoomed out seeing nothing? Is Space (center on selection) discoverable? | __ /5 |
| **2:00** | Economy barely started. 180g is extremely tight — one Barracks costs 120g+80w, leaving almost nothing. | Might have placed Barracks but can't afford soldiers yet. | **Is the resource crunch communicated?** Nova can't build AND train with 180g. Does the UI show "can't afford" clearly? Are build buttons greyed out with costs visible? | __ /5 |
| **4:00** | **Incident 1.** Tension drift is 0.007 (fastest). Enemies are hardest baseline (+6% HP, +5% ATK). | Probably has 0-1 soldiers. | **Guaranteed death?** Is it actually possible to survive incident 1 on Hard with no RTS experience? If not, does the game acknowledge this? | __ /5 |
| **4:30** | Defeat. All buildings destroyed. | "Well, that was fast." | **Is the defeat graceful?** Does the game say something useful? Suggest Easy? Show a minimal "here's what you needed" summary? Or just "Defeat" with no context? | __ /5 |

### Nova × Hard: Critical UX Failures to Watch For
- [ ] Nova can't find their own base on the 256×256 map
- [ ] Defeat feels punishing rather than educational
- [ ] No suggestion to try an easier difficulty
- [ ] Game-over screen provides zero actionable feedback
- [ ] Nova uninstalls

---

## Scenario 4: Meridian × Easy

**A competent player relaxing on Easy. Testing whether the game rewards mastery or bores experts.**

> *"I know the basics. Easy should be my playground — let me experiment with formations."*

### Starting State
- 300g, 150w, 4 workers
- Knows the gather → build → train loop
- Discovered 2 formations (Rose and Spiral)
- Comfortable with stances, understands enemy types

### Journey Checkpoints

| Time | What Happens | What Meridian Does | UX Question | Score |
|---|---|---|---|---|
| **0:00** | Game starts. Meridian immediately sends workers to gather, places Barracks. | Efficient opening. 2 workers on gold, 1 on wood, 1 building. | **Does the game reward speed?** Are the hotkeys responsive? Does the build placement snap cleanly? Any friction in the opening build order? | __ /5 |
| **3:00** | Barracks done. Training soldiers and archers. Starting second Barracks or Tower. | Queuing units, setting rally points, planning base layout. | **Is multi-building management smooth?** Can Meridian select Barracks, queue, tab to next building, queue again without losing selection flow? Are rally points visible? | __ /5 |
| **5:00** | Incident 1 (Easy). Meridian has 3-4 soldiers, maybe 2 archers. Easy fight. | Positions army, maybe uses a formation. Watches combat. | **Is Easy too easy for Meridian?** If combat is trivial, does the game bore them? Is there anything to learn even when winning easily? Does harmony quality feedback encourage experimentation? | __ /5 |
| **10:00** | Incidents 2-3. Meridian is over-prepared. Economy strong. Experimenting. | Trying formation switches mid-combat. Testing Sierpinski vs Koch. Exploring the map. | **Formation experimentation UX.** Can Meridian switch formations smoothly (F1-F4)? Is the visual feedback clear enough to see the difference? Can they compare harmony quality between formations? | __ /5 |
| **15:00** | Mid-game. Meridian is pushing toward discovering formations 3-4. | Moving groups of free military to trigger discovery. Testing compositions. | **Is formation discovery guided enough?** Meridian knows formations exist but may not know the exact recipe for Sierpinski/Koch. Are hints visible? Is the "move 3+ free military together" mechanic intuitive? | __ /5 |
| **20:00** | Incidents 5-6. All 4 formations discovered (hopefully). Mixed squad compositions. | Micro-managing multiple squads. Using stances contextually. | **Multi-squad management.** Tab to cycle squads, 1-9 hotkeys, squad bar clicking. Is this smooth? Can Meridian coordinate 2-3 squads in combat without losing track? | __ /5 |
| **25:00** | Incident 7 (final). Meridian is dominant. Grand assault composition. | Watching the final wave with satisfaction. | **Does victory feel earned?** Even on Easy, does the final wave have drama? Or is it anticlimactic? Does the victory screen show anything interesting (stats, harmony achieved, formations used)? | __ /5 |

### Meridian × Easy: Critical UX Failures to Watch For
- [ ] Easy is so trivial that Meridian never engages with formations seriously
- [ ] Formation discovery hints are invisible — Meridian doesn't find formations 3-4
- [ ] Multi-squad management is clunky (tab cycling, squad bar, hotkeys don't work smoothly)
- [ ] Harmony quality is displayed but Meridian can't figure out how to improve it
- [ ] No incentive to replay Easy — Meridian immediately moves to Medium with nothing learned

---

## Scenario 5: Meridian × Medium

**The intended experience. This is where the game should shine.**

> *"This feels right — I have to think, but I know enough to think WITH."*

### Starting State
- 200g, 100w, 3 workers
- Knows fundamentals. Has beat Easy.
- 14 incidents to survive

### Journey Checkpoints

| Time | What Happens | What Meridian Does | UX Question | Score |
|---|---|---|---|---|
| **0:00** | Tighter start. 3 workers. 128×128 map — four times larger than Easy. | Efficient opening but feels the resource pressure. Decisions matter more. | **Does the difficulty increase feel fair?** Less resources + faster waves should feel like "I need to be sharper" not "the game cheated me." Is the 200g start viable for a Barracks-first opening? (120g+80w = most of the starting pool) | __ /5 |
| **4:30** | Incident 1 (faster than Easy). Meridian has a small army. Should survive but it's close. | Positions carefully. Uses defensive stance. Maybe one formation active. | **Is the first-incident timing fair?** 270s vs 300s on Easy. Meridian should feel pressure but not despair. Does the 30s difference matter? | __ /5 |
| **8:00** | Incidents 2-3. Fade Rangers appear (incident 2). Raiders at incident 4 incoming. Medium starts showing teeth. | Adapting composition. Training archers to counter Fade Rangers. Placing towers near economy. | **Is the counter-pick system readable?** When Fade Rangers appear, does Meridian understand they need soldiers/towers to deal with ranged threats? Is the enemy inspection panel useful in the heat of combat? | __ /5 |
| **12:00** | Incidents 4-6. Raiders targeting workers. Siege (Hexweaver) at incident 6. The Dark 7 diversity increasing. | Multi-front defense. Splitting army. Using Hunt stance to auto-target Raiders. Economic recovery between waves. | **Multi-front pressure.** With 128×128 map and multi-directional spawns, does the minimap give enough warning? Can Meridian react in time? Is the attack notification clear enough? | __ /5 |
| **18:00** | Incidents 7-9. Shieldbearers and Bloodtithe appear. Army composition matters critically now. | Flanking Ironbark. Focusing Bloodtithe. Formation abilities becoming important. | **Specialist enemy readability.** Can Meridian visually distinguish Ironbark from regular soldiers? Is the frontal armor mechanic visible (shield direction indicator)? Does Bloodtithe look/behave differently from regular enemies? | __ /5 |
| **25:00** | Incidents 10-12. Thornknight elites arrive (incident 12). Scaling is steep. Meridian's veterans matter. | Managing veterancy. Protecting high-rank units. Using formations at full capacity. Multiple squads coordinating. | **Veteran unit value.** Can Meridian identify which units are high-rank (visual pips, colors)? Is the rank-up notification clear? Does losing a Sergeant feel devastating (it should)? | __ /5 |
| **35:00** | Incidents 13-14 (final). Maximum enemy diversity. Grand assault. All 7 Dark 7 types potentially present. | Full orchestration. Every system engaged: formations, stances, focus fire, garrison, towers, economy. | **The crescendo.** Does the final stretch feel like a climax? Is the player's mastery tested in a way that feels rewarding? Does everything come together — or does it feel like chaos? | __ /5 |
| **End** | Victory or defeat. Close game either way. | Reviews stats. | **Post-game reflection.** Does the end screen show enough data for Meridian to understand their performance? Kill/death ratio, formations used, economy efficiency, harmony stats? Does it motivate another run? | __ /5 |

### Meridian × Medium: Critical UX Failures to Watch For
- [ ] Resource crunch on opening is too tight — Meridian can't build Barracks + train before incident 1
- [ ] Enemy type diversity overwhelms (too many new types introduced too fast)
- [ ] Multi-directional attacks feel unfair (not enough warning / minimap feedback)
- [ ] Formation harmony system is present but irrelevant to winning (bonuses too small to matter)
- [ ] Specialist enemies (Ironbark, Bloodtithe, Hexweaver) are not visually distinct enough
- [ ] Mid-game slog — incidents 6-10 feel repetitive

---

## Scenario 6: Meridian × Hard

**The wall. Meridian knows the game but Hard should push them to breaking point.**

> *"I can do this. I've beaten Medium. How much harder can it— oh no."*

### Starting State
- 180g, 100w, 3 workers
- 256×256 map — massive, intimidating
- First incident at 240s (4 min)
- 21 incidents to win

### Journey Checkpoints

| Time | What Happens | What Meridian Does | UX Question | Score |
|---|---|---|---|---|
| **0:00** | Huge map. Tight resources. Meridian knows the game but the scale is different. | Scouts with camera. Looks for nearby resources. Tighter build order. | **Does Hard's map size add strategy or confusion?** 256×256 means resources are further apart, defense perimeter is larger, scouting matters. Does the minimap scale well? | __ /5 |
| **4:00** | Incident 1. Hard's scaling is punishing: +6% HP, +5% ATK per incident, and tension drift is 0.007. | Meridian has a small army, uses it well. Barely survives. | **Is the scaling curve fair?** Hard should be hard, not cheap. Does Meridian lose because they made mistakes, or because the numbers are impossible? | __ /5 |
| **10:00** | Incidents 3-5. Siege unlocks at incident 5 (earlier than Medium's 6). Raiders at 3. The unlock gates are compressed. | Adapting faster. Economy under pressure. Every unit matters. | **Compressed unlock curve.** All enemy types arrive faster on Hard. Does this feel like "rising challenge" or "random unfair spikes"? | __ /5 |
| **20:00** | Incidents 7-9. Healer/Bloodtithe unlocks at 9. All types except Elite now in play. Scaling is steep. | Full formation play. Every mistake costs a building or a veteran. | **Error punishment.** On Hard, mistakes are expensive. Is the feedback loop fast enough? Does Meridian understand WHY they lost a building? Was the enemy warning clear? | __ /5 |
| **30:00** | Incidents 10-14. Elite Thornknights arrive at 14. The endgame grind. Scaling means enemies have ~70-84% more HP than base. | Precision micro. Formation switching in combat. Exploiting terrain, towers, flanking. | **Does the game support high-skill play?** Are the controls responsive enough for clutch micro? Can Meridian issue commands fast enough? Any input lag or selection bugs under pressure? | __ /5 |
| **45:00** | Incidents 15-21. The marathon. Hard requires endurance — 21 incidents is three times Easy. | Maintaining concentration. Economy must be perfect. Army must grow continuously. | **Is 21 incidents too many?** Does the late game become repetitive? Or does each incident still introduce pressure? Does the adaptive difficulty engine keep it interesting? | __ /5 |
| **End** | Victory (rare) or defeat (likely around incident 12-16 on first attempt). | Exhaustion or triumph. | **Does Hard defeat teach mastery?** When Meridian loses at incident 14, do they know what to do differently? Is the event log / end screen detailed enough for a motivated player to improve? | __ /5 |

### Meridian × Hard: Critical UX Failures to Watch For
- [ ] Hard feels impossible rather than challenging (numbers too high, not enough player agency)
- [ ] 21 incidents is a slog — the game runs 45+ minutes with repetitive middle acts
- [ ] 256×256 map makes multi-front defense feel random (attacks from too many angles)
- [ ] Adaptive difficulty engine either doesn't kick in (Meridian struggles but no help) or over-corrects
- [ ] The unlock compression means Meridian faces Ironbark before they've learned to counter basic enemies

---

## Scenario 7: Zenith × Easy

**The speedrun. 1500 hours means Easy is a training dummy.**

> *"Easy in 4 minutes. Let's see if the new content breaks anything."*

### Starting State
- 300g, 150w, 4 workers
- Zenith knows optimal build orders, every hotkey, every enemy behavior

### Journey Checkpoints

| Time | What Happens | What Zenith Does | UX Question | Score |
|---|---|---|---|---|
| **0:00** | Instant: 2 workers gold, 1 wood, 1 builds Barracks. Zero thought. | Muscle memory. Hotkeys. No mouse on bottom panel. | **Does the game stay out of the way?** No unnecessary animations blocking input. No confirmation dialogs. No "are you sure" prompts. Hotkeys responsive on frame 1. | __ /5 |
| **1:00** | Barracks placed before 60s. First soldier queued immediately. Worker on iron. | Optimal gather rotation. Already knows where resources are on 64×64 maps. | **Is the early game skippable?** Not literally, but does it flow so fast that Zenith barely notices it? Or are there forced waits (training times, build times) that feel like dead time? | __ /5 |
| **3:00** | Army building. Zenith is already planning squad compositions. | Queuing soldiers and archers in ratios they know produce good harmony. | **Advanced information access.** Does Zenith have access to exact harmony %, exact HP/ATK numbers, exact enemy spawn timing? Or is this information hidden behind clicks? | __ /5 |
| **5:00** | Incident 1. Zenith annihilates it without moving the camera. Towers + positioned army. | Barely engages. Tab to check enemy composition for counter-picking info. | **Is Easy boring for Zenith?** This is expected — Easy SHOULD be trivial for 1500h. But is there anything for Zenith to optimize? Fastest clear time? Maximum economy? Formation experiments? | __ /5 |
| **End** | Victory in 12-15 minutes. Dominant. Never in danger. | Checks stats, compares to previous runs. | **Does the end screen support speedrunning/optimization?** Time, kill count, efficiency metrics, personal bests? Or just "Victory"? | __ /5 |

### Zenith × Easy: Critical UX Failures to Watch For
- [ ] Forced animations or pauses slow down optimized play
- [ ] Information Zenith needs (exact numbers, timers) requires too many clicks
- [ ] No speed/efficiency metrics to chase — Easy has zero replayability for veterans
- [ ] Hotkey conflicts or input priority bugs surface at high APM

---

## Scenario 8: Zenith × Medium

**The warm-up. Zenith plays Medium to test new content before Hard.**

> *"Medium is where I benchmark new patches. Show me if the balance changed."*

### Starting State
- 200g, 100w, 3 workers
- Zenith has optimized Medium builds. Knows exact timing windows.

### Journey Checkpoints

| Time | What Happens | What Zenith Does | UX Question | Score |
|---|---|---|---|---|
| **0:00** | Tight opening. 200g means Barracks costs 60% of gold. Every second matters. | Optimized build order. Workers split instantly. First Barracks at ~50s. | **Is the build order ceiling high enough?** Can Zenith meaningfully outperform a good player through micro-optimization? Or does everyone hit the same economy ceiling regardless of skill? | __ /5 |
| **4:30** | Incident 1. Zenith has 4-5 military, formation active, positioned perfectly. | Clean defense. Already reading enemy composition for future counter-picks. | **Enemy composition telegraph.** Can Zenith see what's in the wave BEFORE it arrives? (Minimap, spawn preview, composition display?) Or must they react after seeing units? | __ /5 |
| **10:00** | Incidents 3-5. Zenith is comfortably ahead. Testing new enemy behaviors (Bloodtithe, Hexweaver post-rename). | Inspecting new enemy types. Testing how Bloodtithe behaves differently from old Marrowmend. | **Content update validation.** After the Dark 7 rework, do the renamed enemies behave correctly? Are tooltips accurate? Do display names show properly? | __ /5 |
| **20:00** | Incidents 8-10. Zenith is experimenting with formation compositions for maximum harmony. | Switching formations mid-combat. Testing Rose sweep against grouped enemies. Spiral tighten/loosen. | **Formation combat responsiveness.** At Zenith's speed, do formation switches happen instantly? Does Rose rotation start/stop cleanly? Does Ctrl+scroll Spiral adjustment feel precise? | __ /5 |
| **30:00** | Incidents 12-14 (final). Zenith is dominant but the scaling means it's not trivial. | Full multi-squad orchestration. Perfect economy. Exploiting every system. | **System ceiling.** Is there a point where Zenith has "solved" Medium and is just waiting? Or does every incident still require active decision-making? | __ /5 |
| **End** | Victory. Clean. Zenith checks event log CSV after. | Opens `logs/` folder. Reads CSV. Compares kill rates, economy efficiency, formation uptime. | **Post-game data.** Is the CSV comprehensive enough for Zenith's analysis? Are there metrics Zenith wants that aren't logged? (Formation harmony over time, DPS breakdown per squad, per-enemy-type kill efficiency?) | __ /5 |

### Zenith × Medium: Critical UX Failures to Watch For
- [ ] Medium is "solved" by Zenith and offers no challenge after incident 5
- [ ] Formation commands have input lag or animation delays that frustrate high-APM play
- [ ] New content (Dark 7 rework) has stale tooltips, wrong labels, or inconsistent naming
- [ ] Event log CSV is missing data Zenith needs for post-game analysis
- [ ] Squad management with 3+ squads has selection or hotkey bugs

---

## Scenario 9: Zenith × Hard

**The real game. This is what 1500 hours has been building toward.**

> *"Hard is the only mode that respects me. Let's see if the balance patch changed anything."*

### Starting State
- 180g, 100w, 3 workers
- 256×256 map, 21 incidents, fastest scaling, earliest unlocks
- Zenith has beaten this before but it's never routine

### Journey Checkpoints

| Time | What Happens | What Zenith Does | UX Question | Score |
|---|---|---|---|---|
| **0:00** | Frame-perfect opening. Workers split to gold/wood/build before the camera finishes loading. | Optimized build: Barracks first, soldier training at ~55s, second worker trained simultaneously. | **Frame-1 responsiveness.** Can Zenith issue commands during the first frame? Any loading delay? Camera start position correct? Workers immediately selectable? | __ /5 |
| **2:00** | Economy fragile. 180g is tight. Barracks + 1 soldier queued = almost bankrupt. | Micro-managing gather routes. Every trip matters. Pulling builder worker to gather after Barracks placement. | **Economy micro ceiling.** Can Zenith optimize gather routes (closest tree, shortest walk to TH)? Does the game support this level of micro? Or do all workers gather at the same rate regardless of player input? | __ /5 |
| **4:00** | Incident 1. Hard's tension drift (0.007) means it arrives FAST. Zenith has 2-3 soldiers, maybe 1 archer. | Pixel-perfect positioning. Using Town Hall garrison for stone-throwing damage. Every HP point matters. | **Garrison micro.** Can Zenith garrison workers AND ungarrison them after the wave with minimal clicks? Is the garrison damage meaningful at this stage? Does the Sentinel's Cry tower interact correctly? | __ /5 |
| **8:00** | Incidents 2-3. Fade Rangers at 2, Raiders at 3. Hard's compressed unlock means diverse threats early. | Counter-building. Training archers for Rangers. Using Hunt stance to auto-target Raiders. Tower placement for coverage. | **Counter-pick speed.** When Zenith sees Fade Rangers in incident 2, can they train archers fast enough for incident 3? Is the Barracks queue responsive? Can they queue mixed units efficiently (T, E, T, E)? | __ /5 |
| **15:00** | Incidents 5-7. Hexweaver (siege, 2x building damage) arrives at 5. Ironbark (shieldbearer) at 6. | Splitting army: anti-siege team near buildings, flanking squad for Ironbark. Formation abilities active. | **Multi-squad precision.** With 2-3 squads, Zenith needs instant switching (Tab/1-9), precise movement commands, clean formation ability activation (V key contextual to formation). Any friction here is catastrophic at this skill level. | __ /5 |
| **25:00** | Incidents 9-12. Bloodtithe (healer) at 9. Full Dark 7 roster approaching. Scaling means enemies have ~50-60% more HP than base. | Focus-fire priority: Bloodtithe first, then Hexweaver, then Thornknight. Staggered engagement to avoid being overwhelmed. | **Target priority UX.** Can Zenith right-click specific enemies reliably in a crowd? Are unit hitboxes correct? Is there a priority-attack command? Or does Zenith lose DPS because they can't click the right enemy? | __ /5 |
| **35:00** | Incidents 14-17. Thornknights (elite) arrive at 14. Adaptive difficulty is tracking Zenith — if they're dominating, scaling increases. | Everything at maximum. Economy producing continuously. Veterancy matters — Zenith's Captains are surgical. Formations providing meaningful bonuses. | **Adaptive difficulty fairness.** If Zenith is playing perfectly and the adaptive engine STILL ramps harder... does it feel challenging or punishing? Is there a ceiling where perfect play guarantees victory? Or can scaling outrun the player? | __ /5 |
| **45:00** | Incidents 18-21 (endgame). Maximum scaling. Enemies have ~100%+ extra HP/ATK. Grand assault waves. | Peak performance. Every system interacting. Micro, macro, formation, economy, veterancy, stances — all at once. | **Does Hard have a skill ceiling?** Can Zenith beat incident 21 through pure skill? Or is there a point where the numbers are impossible regardless of play? (If so, that's a balance problem, not UX.) | __ /5 |
| **End** | Victory or defeat. Either way, Zenith spent 45-60 minutes in full concentration. | Immediately opens CSV. Compares run to previous runs. Looks for efficiency improvements. | **Endgame data richness.** Does the CSV + end screen provide: DPS per squad, formation harmony timeline, resource efficiency ratio, per-incident breakdown, kill/loss ratio per enemy type? Zenith wants ALL the data. | __ /5 |

### Zenith × Hard: Critical UX Failures to Watch For
- [ ] Input lag or selection bugs at high APM (the #1 killer of competitive play)
- [ ] Target priority clicking in crowds is unreliable (hitbox issues)
- [ ] Adaptive difficulty over-scales and makes Hard literally impossible
- [ ] 21 incidents at Hard's pace = 60+ minute games with zero downtime — is this sustainable or exhausting?
- [ ] Squad management with 4+ squads has tab-cycling or hotkey conflicts
- [ ] Post-game data is insufficient for serious optimization (missing per-squad, per-incident breakdowns)
- [ ] 256×256 map creates camera management overhead that adds frustration, not strategy

---

## Scoring Summary

After running all 9 scenarios, fill in the matrix:

```
              EASY    MEDIUM    HARD    AVG
Nova          __/75   __/35     __/20   __/130
Meridian      __/35   __/40     __/30   __/105
Zenith        __/25   __/30     __/40   __/95
              __/135  __/105    __/90   __/330
```

### Priority Triage

| Score Range | Interpretation | Action |
|---|---|---|
| **1-2 avg across scenario** | UX is broken for this player×difficulty | Fix before shipping |
| **2-3 avg** | UX works but has significant friction | Fix in next patch |
| **3-4 avg** | UX is functional, minor polish needed | Backlog for quality pass |
| **4-5 avg** | UX is smooth | Ship it |

### Cross-Scenario Patterns to Watch

| Pattern | What It Means |
|---|---|
| Nova scores low across ALL difficulties | Onboarding is broken — the game doesn't teach itself |
| Easy scores low across ALL archetypes | Easy mode isn't serving its purpose (playground for new, lab for mid, speedrun for veteran) |
| Hard scores low for Meridian AND Zenith | Hard isn't fairly challenging — it's just unfair |
| Zenith scores low on Easy/Medium but high on Hard | Game only works at high skill — casual UX is neglected |
| Meridian scores consistently 3 across everything | The game is functional but unremarkable — needs more personality in the UX |
| Formation checkpoints score low everywhere | Formation UX needs dedicated rework |
| First-incident checkpoints score low everywhere | The onboarding ramp needs work |

---

## How to Use This Document

1. **Before a UX pass:** Run through each scenario mentally (or with a tester). Score each checkpoint honestly.
2. **After changes:** Re-score affected checkpoints. Track improvement.
3. **Prioritize:** Fix the lowest-scoring checkpoints first. A Scenario 1 (Nova×Easy) score of 1 is more urgent than a Scenario 9 (Zenith×Hard) score of 3 — the new player experience gates everything.
4. **Add checkpoints:** As new features ship (Sentinels, formations 5-7, harmony tiers), add checkpoints to the relevant scenarios.
5. **Expand archetypes:** When Healer/Shield/Knight ship, Meridian's journey changes. When Layer 7 content ships, Zenith's journey changes. Update the scenarios.

The matrix grows with the game. Like everything else in Resonance — it's a fractal.
