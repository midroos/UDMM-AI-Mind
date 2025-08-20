# UDMM-Cognitive-Framework-2.0

Unified Dynamic Mind Model (UDMM 2.0): نظام وكلاء واعية يجمع بين التنبؤ المتجسد، القصد متعدد المستويات، والمحاكاة الهجينة ثنائية الاتجاه، مع فهم لغوي مؤثر على الهوية.

## المكونات
- **core/**: الوكيل، الهوية الذاتية، نموذج الجسد
- **linguistic/**: الفهم اللغوي + مخططات المفاهيم والقواعد
- **memory/**: الذاكرة طويلة الأمد، الدلالية، العرضية، الجسدية
- **simulation/**: GSM، HybridSimulator، Pattern/Embodied Engines، Rollout
- **envs/**: TrapEnv و NaturalEnv لسيناريوهات الاختبار
- **run_v2.py**: نقطة تشغيل مبسطة

## البدء
```bash
pip install -e .
pytest -q
python -m udmm2.run_v2
```

## الحالة

نسخة أولية (scaffold). سيتم توسيع الوظائف تباعًا.

---

## Experiments & Visualization

To run an experiment and visualize the agent's learning dynamics (prediction error, precision gain, rule confidence):

```bash
# Ensure you have installed the visualization dependencies
pip install -e .[viz]

# Run the visualization script
python -m scripts.visualize_learning
```

This will run a 60-step simulation and generate plots showing how the agent's internal metrics change over time.

### Virtual Attractor

The agent can be given a goal state in its 2D environment by setting a "Virtual Attractor". This creates a "pull" that influences the agent's action selection, causing it to move towards the target.

To visualize this behavior:

```bash
python -m scripts.visualize_attractor
```
