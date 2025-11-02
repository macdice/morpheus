# Morpheus - Spanish Verb Conjugation Engine

A complete morphology engine for Spanish verb conjugation with support for 100+ verbs, all tenses, moods, and stem changes.

## ✨ Features

✅ **Complete subjunctive system**
  - Present subjunctive (hable, coma, viva)
  - Imperfect subjunctive -ra form (hablara, comiera, viviera)
  - Imperfect subjunctive -se form (hablase, comiese, viviese)

✅ **All stem-change patterns**
  - e→ie (pensar→pienso, querer→quiero)
  - o→ue (poder→puedo, encontrar→encuentro)
  - e→i (pedir→pido, servir→sirvo)
  - u→ue (jugar→juego)

✅ **107 verbs in lexicon** - most common Spanish verbs

✅ **Conventional ordering** - 1sg, 2sg, 3sg, 1pl, 2pl, 3pl

## 🚀 Quick Start

```bash
python3 demo.py
```

## 📖 Example

```python
from morpheus import MorphologyEngine

engine = MorphologyEngine()
engine.load_morphology('es.morphology')
engine.load_lexicon('es.lexicon')

forms = engine.conjugate('poder')
print(forms['present subjunctive']['1sg'])  # pueda
print(forms['imperfect subjunctive -ra']['1sg'])  # podiera
print(forms['imperfect subjunctive -se']['1sg'])  # podiese
```

## 📊 Verb Coverage

- 32 regular -ar verbs
- 21 regular -er verbs  
- 14 regular -ir verbs
- 33 stem-changing verbs
- 7 orthographic change verbs

Total: **107 verbs**
