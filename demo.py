#!/usr/bin/env python3
"""
Morpheus Demo - Spanish Verb Conjugation Engine
Demonstrates all features including subjunctives and stem changes
"""

from morpheus import MorphologyEngine

def print_verb_summary(engine, verb):
    """Print a summary of a verb's conjugation"""
    print(f"\n{'='*70}")
    print(f"  {verb.upper()}")
    print('='*70)
    
    conj = engine.conjugate(verb)
    
    # Present Indicative
    if 'present indicative' in conj:
        print("\nPRESENT INDICATIVE")
        for person in ['1sg', '2sg', '3sg', '1pl', '2pl', '3pl']:
            if person in conj['present indicative']:
                print(f"  {person:6} {conj['present indicative'][person]}")
    
    # Present Subjunctive
    if 'present subjunctive' in conj:
        print("\nPRESENT SUBJUNCTIVE")
        for person in ['1sg', '2sg', '3sg', '1pl', '2pl', '3pl']:
            if person in conj['present subjunctive']:
                print(f"  {person:6} {conj['present subjunctive'][person]}")
    
    # Imperfect Subjunctive -ra
    if 'imperfect subjunctive -ra' in conj:
        print("\nIMPERFECT SUBJUNCTIVE (-ra form)")
        for person in ['1sg', '2sg', '3sg', '1pl', '2pl', '3pl']:
            if person in conj['imperfect subjunctive -ra']:
                print(f"  {person:6} {conj['imperfect subjunctive -ra'][person]}")
    
    # Imperfect Subjunctive -se
    if 'imperfect subjunctive -se' in conj:
        print("\nIMPERFECT SUBJUNCTIVE (-se form)")
        for person in ['1sg', '2sg', '3sg', '1pl', '2pl', '3pl']:
            if person in conj['imperfect subjunctive -se']:
                print(f"  {person:6} {conj['imperfect subjunctive -se'][person]}")


def main():
    print("=" * 70)
    print("  MORPHEUS - Spanish Verb Conjugation Engine")
    print("=" * 70)
    
    engine = MorphologyEngine()
    engine.load_morphology('es.morphology')
    engine.load_lexicon('es.lexicon')
    
    print(f"\nLoaded {len(engine.verbs)} verbs from lexicon")
    print(f"Loaded {len(engine.patterns)} conjugation patterns")
    
    # Demonstrate different verb types
    print("\n\n" + "=" * 70)
    print("  DEMONSTRATION: Different Verb Types")
    print("=" * 70)
    
    demos = [
        ('hablar', 'Regular -ar verb'),
        ('comer', 'Regular -er verb'),
        ('vivir', 'Regular -ir verb'),
        ('pensar', 'Stem-changing e→ie (-ar)'),
        ('querer', 'Stem-changing e→ie (-er)'),
        ('poder', 'Stem-changing o→ue (-er)'),
        ('pedir', 'Stem-changing e→i (-ir)'),
        ('jugar', 'Stem-changing u→ue (unique!)'),
    ]
    
    for verb, description in demos:
        print(f"\n{verb} ({description})")
        print("-" * 70)
        conj = engine.conjugate(verb)
        if 'present indicative' in conj:
            print("Present indicative:")
            for person in ['1sg', '3sg', '1pl']:
                print(f"  {person}: {conj['present indicative'][person]}")
        if 'imperfect subjunctive -ra' in conj:
            print("Imperfect subjunctive -ra:")
            for person in ['1sg', '3sg']:
                print(f"  {person}: {conj['imperfect subjunctive -ra'][person]}")
        if 'imperfect subjunctive -se' in conj:
            print("Imperfect subjunctive -se:")
            for person in ['1sg', '3sg']:
                print(f"  {person}: {conj['imperfect subjunctive -se'][person]}")
    
    # Show full conjugation of one verb
    print("\n\n" + "=" * 70)
    print("  COMPLETE CONJUGATION: poder (to be able)")
    print("=" * 70)
    print_verb_summary(engine, 'poder')
    
    print("\n\n" + "=" * 70)
    print("  Statistics")
    print("=" * 70)
    
    # Count verb types
    regular_ar = sum(1 for v in engine.verbs.values() 
                     if v.infinitive.endswith('ar') and not v.properties)
    regular_er = sum(1 for v in engine.verbs.values() 
                     if v.infinitive.endswith('er') and not v.properties)
    regular_ir = sum(1 for v in engine.verbs.values() 
                     if v.infinitive.endswith('ir') and not v.properties)
    stem_changing = sum(1 for v in engine.verbs.values() 
                        if any('stem-change' in p for p in v.properties))
    
    print(f"\nRegular -ar verbs: {regular_ar}")
    print(f"Regular -er verbs: {regular_er}")
    print(f"Regular -ir verbs: {regular_ir}")
    print(f"Stem-changing verbs: {stem_changing}")
    print(f"\nTotal: {len(engine.verbs)} verbs")
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
