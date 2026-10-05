# axiom-stack v0.2.0

Meta-repository и воспроизводимый reference pipeline для **Autopoietic Proof-Carrying Computing**.

## Главный скачок v0.2

Reference path больше не доказывает `abs` перебором конечного диапазона. `axiom-cegis` получает контрпримеры от
`axiom-symbolic`, пока не синтезирует программу, которая символически корректна для **всех математических целых в
поддерживаемом одномерном affine-фрагменте**.

Запуск из этого репозитория при наличии соседних репозиториев:

```bash
python reference-v0.2.py
```

Скрипт также проверяет отказ после подмены proof-bound программы и запускает KV-эксперимент архитектурной эволюции.

## Связанные исследования

Этот компонент входит в исследовательский проект [Axiom](https://github.com/localzet/axiom-stack). Все компоненты собраны по теме [localzet-axiom](https://github.com/topics/localzet-axiom). Основной язык документации — русский. Исследовательские результаты и ограничения не означают готовность к промышленному применению.

## Компоненты и воспроизведение

`components.json` фиксирует проверенные коммиты всех 15 соседних компонентов. Этот метарепозиторий — шестнадцатый компонент. Зафиксированные версии воспроизводятся без привязки к путям конкретного компьютера:

```sh
git clone https://github.com/localzet/axiom-stack.git axiom/axiom-stack
cd axiom/axiom-stack
python3 bootstrap.py --directory ..
python3 reference-smoke.py
python3 reference-v0.2.py
```

Скрипт не меняет существующий репозиторий с другой версией или незакоммиченными файлами: используйте новую пустую папку для воспроизводимого эксперимента. Для Rust-компонентов выполняйте `cargo test --locked --all-targets`, для `axiom-symbolic` и `axiom-cegis` — `python3 -m unittest discover -s tests -v` в соответствующей папке. Формальные результаты проверяются командой `lake build` в `axiom-formal` на Lean из `lean-toolchain`.

Конечные обучающие примеры сами по себе не доказывают обобщение синтезированной программы. Символический backend поддерживает ограниченный одномерный аффинный фрагмент; другие конструкции должны отклоняться. Теоремы Lean проверяют модель, а соответствие VM этой модели ещё предстоит доказать. Эксперимент KV не является промышленной базой данных.

## Карта исследований

- [axiom-capabilities](https://github.com/localzet/axiom-capabilities)
- [axiom-cegis](https://github.com/localzet/axiom-cegis)
- [axiom-formal](https://github.com/localzet/axiom-formal)
- [axiom-ir](https://github.com/localzet/axiom-ir)
- [axiom-kv-lab](https://github.com/localzet/axiom-kv-lab)
- [axiom-node](https://github.com/localzet/axiom-node)
- [axiom-proof](https://github.com/localzet/axiom-proof)
- [axiom-research](https://github.com/localzet/axiom-research)
- [axiom-runtime](https://github.com/localzet/axiom-runtime)
- [axiom-solver](https://github.com/localzet/axiom-solver)
- [axiom-spec](https://github.com/localzet/axiom-spec)
- [axiom-symbolic](https://github.com/localzet/axiom-symbolic)
- [axiom-synth](https://github.com/localzet/axiom-synth)
- [axiom-verifier](https://github.com/localzet/axiom-verifier)
- [axiom-zk-bridge](https://github.com/localzet/axiom-zk-bridge)

## Авторство

Сопровождающий собственных изменений: **Ivan Zorin (localzet)** — <creator@localzet.com> · https://www.localzet.com. Copyright © 2026 Localzet Group. Исходное авторство и лицензии сторонних компонентов сохраняются. См. [AUTHORS](.github/AUTHORS.md).
