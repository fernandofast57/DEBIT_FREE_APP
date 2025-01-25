
# Standards di Sviluppo

## Naming Conventions
- Seguire strettamente il glossario in `docs/GLOSSARY.md`
- Usare i nomi delle classi e metodi come definiti nel glossario
- Mantenere coerenza con gli stati delle transazioni definiti

## Validazione Automatica
- Ogni commit viene validato automaticamente
- Il middleware `glossary_compliance_checker.py` verifica la conformità
- I test devono passare la validazione del glossario

## Procedure di Review
1. Verificare la conformità con il glossario
2. Controllare la standardizzazione dei nomi
3. Validare gli stati delle transazioni
4. Confermare la coerenza dei messaggi di log
