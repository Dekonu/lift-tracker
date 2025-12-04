# Periodization Research Summary

## Overview
Periodization is the systematic planning of training variables (volume, intensity, frequency) over time to optimize performance and prevent overtraining.

## Three Main Types

### 1. Linear Periodization
**Concept**: Progressive increase in intensity while decreasing volume over time.

**Structure**:
- **Weeks 1-4**: High volume (3-5 sets × 8-12 reps), moderate intensity (60-70% 1RM)
- **Weeks 5-8**: Moderate volume (3-4 sets × 5-8 reps), higher intensity (75-85% 1RM)
- **Weeks 9-12**: Lower volume (2-3 sets × 1-5 reps), high intensity (85-95% 1RM)

**Best For**: Beginners, general strength building, peaking for competition
**Pros**: Simple, predictable, good for learning form
**Cons**: Can lead to plateaus, less variety

**Example Program**:
- Week 1-4: 4 sets × 10 reps @ 65% 1RM
- Week 5-8: 3 sets × 6 reps @ 80% 1RM
- Week 9-12: 2 sets × 3 reps @ 90% 1RM

### 2. Undulating Periodization (DUP - Daily Undulating Periodization)
**Concept**: Frequent variation of volume and intensity within the same week.

**Structure**:
- **Day 1**: High volume, moderate intensity (4 sets × 8 reps @ 70% 1RM)
- **Day 2**: Moderate volume, high intensity (3 sets × 5 reps @ 85% 1RM)
- **Day 3**: Low volume, very high intensity (2 sets × 3 reps @ 90% 1RM)

**Best For**: Intermediate/advanced lifters, those training 3+ days/week
**Pros**: Prevents adaptation, maintains variety, can train multiple qualities
**Cons**: More complex, requires careful planning

**Example Program (3 days/week)**:
- Monday: 4 sets × 10 reps @ 70% 1RM
- Wednesday: 3 sets × 5 reps @ 85% 1RM
- Friday: 2 sets × 3 reps @ 90% 1RM
- Repeat weekly with slight progression

### 3. Block Periodization
**Concept**: Focused training blocks (mesocycles) targeting specific adaptations.

**Structure**:
- **Block 1 (4-6 weeks)**: Accumulation - High volume, moderate intensity (hypertrophy focus)
- **Block 2 (3-4 weeks)**: Transmutation - Moderate volume/intensity (strength focus)
- **Block 3 (2-3 weeks)**: Realization - Low volume, high intensity (peaking)

**Best For**: Advanced athletes, competition preparation, specific goal phases
**Pros**: Highly specific, allows deep adaptation, great for peaking
**Cons**: Requires longer planning, less variety within blocks

**Example Program**:
- Weeks 1-6: 5 sets × 8 reps @ 70% 1RM (Accumulation)
- Weeks 7-10: 4 sets × 5 reps @ 80% 1RM (Transmutation)
- Weeks 11-13: 3 sets × 2 reps @ 92% 1RM (Realization)

## Weight Specification Methods

### Static Weights
- Fixed weight for all sets (e.g., 225 lbs for all sets)
- Simple, consistent
- Best for: Linear periodization, beginners

### Percentage-Based
- Weight calculated as percentage of 1RM (e.g., 80% of 1RM)
- Automatically adjusts if 1RM changes
- Best for: All periodization types, progressive overload

### RPE-Based (Rate of Perceived Exertion)
- Weight selected based on target RPE (e.g., RPE 8 = 2 reps in reserve)
- Auto-regulates based on daily readiness
- Best for: Advanced lifters, autoregulation

### RIR-Based (Reps in Reserve)
- Similar to RPE, specifies how many reps left in the tank
- More intuitive for some users
- Best for: Intermediate/advanced lifters

## UI Design Recommendations

### Template Builder Interface
1. **Exercise Selection**: Search/select from exercise library
2. **Set Configuration**: 
   - Number of sets
   - Reps per set (or rep range)
   - Weight type (static, percentage, RPE, RIR)
   - Rest periods
3. **Periodization Presets**: 
   - Auto-generate sets based on periodization type
   - Allow manual override
4. **Visual Preview**: Show how sets change across weeks

### Program Week Assignment
1. **Week View**: Grid showing all weeks in program
2. **Template Assignment**: Drag-and-drop or click to assign templates
3. **Periodization Visualization**: Color-coded intensity/volume indicators
4. **Quick Edit**: Modify volume/intensity modifiers per week

### Modern UI Elements
- **Card-based design**: Each exercise in its own card
- **Drag-and-drop**: Reorder exercises and sets
- **Inline editing**: Click to edit, no separate forms
- **Progress indicators**: Visual representation of periodization curve
- **Smart defaults**: Auto-fill based on periodization type
- **Mobile-responsive**: Works on all screen sizes

