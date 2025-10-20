# 🔧 Troubleshooting - Problemas Comuns

## ❌ Erro: Symbol not found xerces-c (macOS)

### Problema
```
dyld: Symbol not found: __ZN11xercesc_3_211InputSourceC2E...
Expected in: /opt/homebrew/Cellar/xerces-c/3.3.0/lib/libxerces-c-3.3.dylib
```

### Causa
O SUMO-GUI foi compilado com uma versão incompatível da biblioteca xerces-c.

### ✅ Solução 1: Usar SUMO sem GUI (RECOMENDADO)

Edite `.env`:
```bash
SUMO_GUI=False
```

Execute normalmente:
```bash
python main.py
```

A simulação roda perfeitamente sem interface gráfica, e você pode ver os logs no terminal.

### ✅ Solução 2: Recompilar SUMO do código-fonte

```bash
# 1. Remover SUMO atual
brew uninstall sumo

# 2. Instalar dependências
brew install cmake python fox proj gdal gl2ps xerces-c

# 3. Clonar repositório SUMO
git clone --depth 1 https://github.com/eclipse-sumo/sumo
cd sumo

# 4. Compilar
export SUMO_HOME="$PWD"
mkdir build/cmake-build
cd build/cmake-build
cmake ../..
make -j$(sysctl -n hw.ncpu)

# 5. Adicionar ao PATH
echo 'export SUMO_HOME="$HOME/sumo"' >> ~/.zshrc
echo 'export PATH="$SUMO_HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### ✅ Solução 3: Usar versão antiga do xerces-c

```bash
# Downgrade xerces-c para versão compatível
brew uninstall xerces-c
brew install xerces-c@3.2

# Relinkar SUMO
brew unlink sumo
brew link --force xerces-c@3.2
brew link sumo
```

### ✅ Solução 4: Usar Docker para SUMO

Crie `docker-compose.yml`:
```yaml
version: '3'
services:
  sumo:
    image: eclipsesumosuite/sumo:latest
    volumes:
      - ./scenarios:/scenarios
    ports:
      - "8813:8813"
    command: sumo -c /scenarios/simple_grid/simulation.sumocfg --remote-port 8813
```

Execute:
```bash
docker-compose up -d
```

## ❌ TraCI não conecta

### Problema
```
Could not connect to TraCI server using port XXXX
```

### Soluções

1. **Verificar se SUMO está no PATH**
```bash
which sumo
sumo --version
```

2. **Testar SUMO manualmente**
```bash
sumo -c scenarios/simple_grid/simulation.sumocfg
```

3. **Verificar arquivo de configuração**
```bash
# Deve existir:
ls -la scenarios/simple_grid/simulation.sumocfg
ls -la scenarios/simple_grid/network.net.xml
```

4. **Usar porta diferente no .env**
```bash
SUMO_PORT=8814
```

## ❌ Prosody não conecta

### Problema
```
Could not connect to XMPP server
```

### Soluções

1. **Verificar se Docker está rodando**
```bash
docker ps | grep prosody
```

2. **Reiniciar Prosody**
```bash
./scripts/setup_prosody.sh
```

3. **Ver logs do Prosody**
```bash
docker logs prosody
```

4. **Registrar agentes manualmente**
```bash
docker exec -it prosody prosodyctl register test localhost senha123
```

## ❌ Import SPADE não encontrado

### Problema
```
ModuleNotFoundError: No module named 'spade'
```

### Solução

1. **Ativar ambiente virtual**
```bash
source venv/bin/activate
```

2. **Reinstalar dependências**
```bash
pip install -r requirements.txt
```

3. **Verificar Python**
```bash
which python
python --version
```

## ❌ Erro Python 3.14 incompatível

### Problema
```
PyO3's maximum supported version (3.13)
```

### Solução

Instalar com flag de compatibilidade:
```bash
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install -r requirements.txt
```

Ou usar Python 3.13:
```bash
brew install python@3.13
rm -rf venv
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## ❌ XQuartz não funciona

### Problema
GUI não abre no macOS

### Solução

1. **Instalar XQuartz**
```bash
brew install --cask xquartz
```

2. **Configurar permissões**
- Abrir XQuartz
- Preferences > Security
- ✅ "Allow connections from network clients"

3. **Configurar DISPLAY**
```bash
export DISPLAY=:0
xhost + localhost
```

4. **Logout e Login** no macOS

## 📊 Como Verificar Se Está Funcionando

### Teste sem GUI (Mais Confiável)

```bash
# 1. Editar .env
SUMO_GUI=False

# 2. Executar
python main.py
```

Você deve ver:
```
INFO - Iniciando SUMO...
INFO - SUMO iniciado com sucesso
INFO - Agente trafficlight_0@localhost iniciado
INFO - Carro car_0 criado: h0_0 -> v2_1
INFO - Step 100: 8 veículos na simulação
```

### Teste com GUI (Se resolver xerces-c)

```bash
# 1. Editar .env
SUMO_GUI=True

# 2. Executar
python main.py
```

Deve abrir janela SUMO com visualização gráfica.

## 🆘 Ainda com problemas?

1. **Verifique versões**
```bash
python --version
sumo --version
docker --version
```

2. **Logs completos**
```bash
python main.py 2>&1 | tee simulation.log
```

3. **Teste componentes separadamente**

```bash
# Testar SUMO
sumo -c scenarios/simple_grid/simulation.sumocfg

# Testar Prosody
docker exec -it prosody prosodyctl status

# Testar Python/SPADE
python -c "import spade; print('SPADE OK')"
python -c "import traci; print('TraCI OK')"
```

## 📝 Reportar Problemas

Se nenhuma solução funcionar, colete estas informações:

```bash
# Informações do sistema
uname -a
python --version
sumo --version
brew list | grep sumo
brew list | grep xerces

# Logs
python main.py 2>&1 | tee debug.log
```

---

**Nota**: Para a maioria dos casos no macOS M1 com xerces-c 3.3.0, usar `SUMO_GUI=False` é a solução mais rápida e confiável.
