# Pokus o lokální prediktor pro DiceWars

## Přístup:
- zaznamenáme všechny útoky AI a jejich úspěšnost v nějakém turnaji (`RecordingServer`) a
  jako tréninková data
- natrénujeme neuronovou síť
- vyhodnotíme očekávanou úspěšnost všech možných útoků, zahodíme příliš
  neúspěšné tahy, ze zbývajících vybereme nejlepší

## Příznaky:
- počty kostek v source i target poli
- pravděpodobnost úspěšného útoku
- pravděpodobnost udržení source pole při současném počtu kostek
- pravděpodobnost udržení source pole pokud tam zůstane jedna kostka
- součet kostek útočníka v 1- a 2-okolí source pole
- součet ostatních kostek v 1- a 2-okolí target pole

## Výstupy:
- P(udržení source pole do začátku dalšího tahu)
- P(udržení target pole do začátku dalšího tahu)

## Instrukce:
- clone into `dicewars/ai/xzaryb00`
- to record turns, replace `Game` in `scripts/server.py`, and run a game
  (e.g. `scripts/dicewars-ai-only.py -l log -n 10 --ai dt.sdc dt.ste dt.stei
  dt.wpm_c dt.rand`)

``` python
from dicewars.ai.xzaryb00.recording_server import RecordingGame as Game
# from dicewars.server.game import Game
```
- to train the model, run e.g. `python dicewars/ai/xzaryb00/trainer.py` -
  assumes `turns.csv` in the current directory and produces a
  `local-predictor.model` file.
- to run the game, revert the change in `scripts/server.py` (`RecordingGame` ->
  `Game`), and run a game (e.g. `scripts/dicewars-ai-only.py -l log -n 10 --ai
  dt.sdc dt.ste dt.stei dt.wpm_c xzaryb00`).
