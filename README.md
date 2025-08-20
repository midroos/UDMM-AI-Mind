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
