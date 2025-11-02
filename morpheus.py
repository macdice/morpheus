#!/usr/bin/env python3
"""
Morpheus - A morphology engine for human languages
Parses .morphology and .lexicon files and conjugates verbs
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from pathlib import Path


@dataclass
class StemAdjustment:
    """Represents a stem transformation like (-ar → ∅) or (e → ie)"""
    pattern: str
    replacement: str
    condition: Optional[str] = None  # e.g., "in final syllable"
    
    def apply(self, text: str) -> str:
        """Apply this adjustment to text"""
        if self.replacement == '∅':
            # Remove the pattern
            if text.endswith(self.pattern.lstrip('-')):
                return text[:len(text) - len(self.pattern.lstrip('-'))]
            return text
        else:
            # Handle ending replacements like -er → ie
            if self.pattern.startswith('-'):
                # This is an ending replacement
                ending = self.pattern.lstrip('-')
                if text.endswith(ending):
                    return text[:-len(ending)] + self.replacement
                return text
            
            # Handle stem changes
            if self.condition == "in final syllable":
                # For stem changes like e→ie, o→ue, e→i, u→ue
                # Find the last occurrence of the pattern vowel and replace it
                # Work backwards to find last occurrence
                for i in range(len(text) - 1, -1, -1):
                    if text[i] == self.pattern:
                        return text[:i] + self.replacement + text[i+1:]
                return text
            return text.replace(self.pattern, self.replacement)


@dataclass
class ConjugationForm:
    """A single conjugated form like '1sg stem -o'"""
    person: str  # e.g., "1sg", "3pl"
    stem_name: str  # e.g., "stem", "changed-stem"
    ending: str  # e.g., "-o", "-amos"


@dataclass
class ConjugationPattern:
    """A complete conjugation pattern for a tense/mood"""
    name: str  # e.g., "present indicative"
    condition: str  # e.g., 'infinitive like "-ar"' or 'stem-change e→ie'
    forms: List[ConjugationForm] = field(default_factory=list)
    stems: Dict[str, List[StemAdjustment]] = field(default_factory=dict)


@dataclass  
class Verb:
    """A verb entry from the lexicon"""
    infinitive: str
    properties: List[str] = field(default_factory=list)  # e.g., ["stem-change e→ie"]


class MorphologyEngine:
    """Parses morphology files and conjugates verbs"""
    
    # Define conventional display order for persons
    PERSON_ORDER = ['1sg', '2sg', '3sg', '1pl', '2pl', '3pl', 'form']
    
    def __init__(self):
        self.patterns: List[ConjugationPattern] = []
        self.verbs: Dict[str, Verb] = {}
    
    @staticmethod
    def _sort_key(person: str) -> int:
        """Return sort key for conventional person order"""
        try:
            return MorphologyEngine.PERSON_ORDER.index(person)
        except ValueError:
            return 999  # Unknown persons go last
        
    def load_morphology(self, filepath: str):
        """Load a .morphology file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse conjugation patterns
        pattern_blocks = re.findall(
            r'define conjugation (.*?) as\n(.*?)\n\s+with\n(.*?)(?=\n\n|define |end morphology)',
            content,
            re.DOTALL
        )
        
        for name_and_cond, forms_text, stems_text in pattern_blocks:
            pattern = self._parse_conjugation_pattern(name_and_cond, forms_text, stems_text)
            self.patterns.append(pattern)
            
        # Parse participles
        participle_blocks = re.findall(
            r'define (.*?-participle) for (.*?) as\n\s+(.*?)\n\s+with (.*?);',
            content,
            re.DOTALL
        )
        
        for participle_type, condition, form_text, stem_text in participle_blocks:
            pattern = ConjugationPattern(
                name=participle_type,
                condition=condition.strip()
            )
            # Parse the simple form (e.g., "stem -ado")
            parts = form_text.strip().split()
            if len(parts) == 2:
                pattern.forms.append(ConjugationForm(
                    person="",
                    stem_name=parts[0],
                    ending=parts[1]
                ))
            # Parse stem definition
            stem_match = re.search(r'(\w+)\s*=\s*infinitive adjusted:\s*\((.*?)\)', stem_text)
            if stem_match:
                stem_name = stem_match.group(1)
                adjustments = self._parse_adjustments(stem_match.group(2))
                pattern.stems[stem_name] = adjustments
            self.patterns.append(pattern)
    
    def _parse_conjugation_pattern(self, name_and_cond: str, forms_text: str, stems_text: str) -> ConjugationPattern:
        """Parse a conjugation pattern block"""
        pattern = ConjugationPattern(name="", condition="")
        
        # Parse name and condition
        parts = name_and_cond.strip().split(' for ')
        pattern.name = parts[0].strip()
        if len(parts) > 1:
            pattern.condition = parts[1].strip()
        
        # Parse forms (e.g., "1sg  stem  -o,")
        for line in forms_text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            line = line.rstrip(',')
            parts = line.split()
            if len(parts) >= 3:
                pattern.forms.append(ConjugationForm(
                    person=parts[0],
                    stem_name=parts[1],
                    ending=parts[2]
                ))
        
        # Parse stem definitions
        for line in stems_text.strip().split('\n'):
            line = line.strip().rstrip(',').rstrip(';')
            if not line or line.startswith('#'):
                continue
            
            # Match patterns like: stem = infinitive adjusted: (-ar → ∅)
            match = re.match(r'(\w+(?:-\w+)?)\s*=\s*infinitive adjusted:\s*\((.*?)\)', line)
            if match:
                stem_name = match.group(1)
                adjustments = self._parse_adjustments(match.group(2))
                pattern.stems[stem_name] = adjustments
                continue
            
            # Match patterns like: changed-stem = base-stem adjusted: (e → ie in final syllable)
            match = re.match(r'(\w+(?:-\w+)?)\s*=\s*(\w+(?:-\w+)?)\s+adjusted:\s*\((.*?)\)', line)
            if match:
                stem_name = match.group(1)
                base_stem = match.group(2)
                adjustments_str = match.group(3)
                
                # Get base stem adjustments and add new ones
                if base_stem in pattern.stems:
                    # Copy base stem adjustments and add new ones
                    base_adjustments = pattern.stems[base_stem].copy()
                    new_adjustments = self._parse_adjustments(adjustments_str)
                    pattern.stems[stem_name] = base_adjustments + new_adjustments
                elif base_stem == 'infinitive':
                    # Just use the new adjustments
                    pattern.stems[stem_name] = self._parse_adjustments(adjustments_str)
                continue
        
        return pattern
    
    def _parse_adjustments(self, text: str) -> List[StemAdjustment]:
        """Parse adjustment rules like '-ar → ∅, -er → ∅'"""
        adjustments = []
        for part in text.split(','):
            part = part.strip()
            if '→' in part:
                pattern, replacement = part.split('→')
                pattern = pattern.strip()
                replacement = replacement.strip()
                
                # Check for conditions
                condition = None
                if ' in final syllable' in replacement:
                    condition = "in final syllable"
                    replacement = replacement.replace(' in final syllable', '').strip()
                
                adjustments.append(StemAdjustment(pattern, replacement, condition))
        return adjustments
    
    def load_lexicon(self, filepath: str):
        """Load a .lexicon file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse verb entries
        verb_lines = re.findall(r'verb\s+(\w+)(?:\s+\((.*?)\))?;', content)
        
        for infinitive, properties in verb_lines:
            props = []
            if properties:
                # Parse properties like "stem-change e→ie"
                props = [p.strip() for p in properties.split(',')]
            self.verbs[infinitive] = Verb(infinitive=infinitive, properties=props)
    
    def conjugate(self, infinitive: str) -> Dict[str, Dict[str, str]]:
        """Conjugate a verb, returning all forms organized by tense/mood"""
        if infinitive not in self.verbs:
            raise ValueError(f"Verb '{infinitive}' not found in lexicon")
        
        verb = self.verbs[infinitive]
        result = {}
        
        for pattern in self.patterns:
            # Check if this pattern applies to this verb
            if not self._pattern_matches(pattern, verb):
                continue
            
            # Generate forms for this pattern
            forms = {}
            for form in pattern.forms:
                # Get the stem
                stem = self._compute_stem(infinitive, form.stem_name, pattern.stems)
                # Add the ending
                conjugated = stem + form.ending.lstrip('-')
                forms[form.person if form.person else "form"] = conjugated
            
            result[pattern.name] = forms
        
        return result
    
    def _pattern_matches(self, pattern: ConjugationPattern, verb: Verb) -> bool:
        """Check if a conjugation pattern applies to a verb"""
        condition = pattern.condition
        
        # Handle empty/universal patterns (future, conditional)
        if not condition or condition.strip() == '':
            return True
        
        # Check for compound conditions with "and"
        if ' and ' in condition:
            # All conditions must be true
            conditions = condition.split(' and ')
            return all(self._check_single_condition(cond.strip(), verb) for cond in conditions)
        
        return self._check_single_condition(condition, verb)
    
    def _check_single_condition(self, condition: str, verb: Verb) -> bool:
        """Check if a single condition applies to a verb"""
        # Check infinitive ending patterns
        if 'infinitive like' in condition:
            endings = re.findall(r'"(-\w+)"', condition)
            for ending in endings:
                if verb.infinitive.endswith(ending.lstrip('-')):
                    return True
            return False
        
        # Check for stem-change patterns
        if 'stem-change' in condition:
            for prop in verb.properties:
                if prop in condition:
                    return True
            return False
        
        return False
    
    def _compute_stem(self, infinitive: str, stem_name: str, stems: Dict[str, List[StemAdjustment]]) -> str:
        """Compute a stem by applying adjustments"""
        if stem_name not in stems:
            # If stem not defined, return infinitive as-is (for patterns like future)
            return infinitive
        
        stem = infinitive
        for adjustment in stems[stem_name]:
            old_stem = stem
            stem = adjustment.apply(stem)
            # DEBUG
            #print(f"  Applying {adjustment.pattern} → {adjustment.replacement} to '{old_stem}' = '{stem}'")
        
        return stem


def main():
    """Demo: load morphology and conjugate some verbs"""
    engine = MorphologyEngine()
    
    # Load files
    engine.load_morphology('es.morphology')
    engine.load_lexicon('es.lexicon')
    
    # Conjugate each verb
    for infinitive in ['hablar', 'comer', 'vivir', 'pensar']:
        print(f"\n{'='*60}")
        print(f"Conjugation of: {infinitive}")
        print('='*60)
        
        conjugations = engine.conjugate(infinitive)
        
        for tense in sorted(conjugations.keys()):
            forms = conjugations[tense]
            print(f"\n{tense.upper()}")
            # Sort by conventional person order
            for person in sorted(forms.keys(), key=engine._sort_key):
                print(f"  {person:6} {forms[person]}")


if __name__ == '__main__':
    main()
