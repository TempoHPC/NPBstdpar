# NPBstdpar: adaptação dos benchmarks NPB para Fortran DO CONCURRENT

Este diretório reúne uma versão adaptada dos benchmarks NAS Parallel Benchmarks (NPB) a partir da base OpenMP original, com a evolução para estruturas de paralelismo expressas em Fortran usando `do concurrent`. A adaptação mantém a estrutura dos kernels clássicos do NPB e modifica a estratégia de paralelização para explorar execução concorrente em nível de laço, com suporte a compilação em CPU e GPU.

## Visão geral

A base original dos benchmarks NPB era orientada a OpenMP, com pragmas e estruturas de paralelização explícitas em loops volumosos. Nesta variante, a abordagem foi convertida para um estilo mais moderno em Fortran, em que laços do tipo `do concurrent` expressam paralelismo de dependência independente e permitem que o compilador gere código eficiente para arquiteturas SIMD, multicore e aceleradoras.

A principal família adaptada é a do benchmark SP (Scalar Penta-diagonal), presente em arquivos como:

- `SP/x_solve.f`
- `SP/y_solve.f`
- `SP/z_solve.f`
- `SP/rhs.f`
- `SP/pinvr.f`
- `SP/ninvr.f`
- `SP/txinvr.f`
- `SP/tzetar.f`
- `SP/add.f`

Esses kernels substituem o modelo OpenMP clássico por loops `do concurrent`, preservando a lógica numérica do problema, mas permitindo que o compilador trate a concorrência de forma mais natural e, em algumas configurações, se aproxime da execução em aceleradores GPU.

## Mudanças principais da adaptação

### 1. Migração de OpenMP para `do concurrent`

A lógica de programação paralela original fazia uso de regiões OpenMP com `parallel do`, `collapse`, `barrier` e sincronização por `nowait`. Na versão adaptada, os kernels foram reescritos para usar loops do tipo:

```fortran
      do concurrent (k = 1:nz2, j = 1:ny2, i = 1:nx2)
         ...
      end do
```

Esse estilo torna explícita a independência das iterações e elimina a necessidade de controle manual de sincronização em muitos casos. O compilador passa a assumir a ausência de dependências de dados entre iterações, o que é apropriado para o padrão computacional do benchmark.

### 2. Inlining de rotinas e redução de overhead

A adaptação também trabalha com a ideia de inlining de rotinas pequenas e auxiliares, especialmente aquelas usadas em hot loops da resolução do SP. Esse procedimento reduz chamadas de função em regiões de alto volume computacional e favorece a compilação em conjunto de código, permitindo melhor exploração do pipeline e menor overhead em execução.

Em outras palavras, a estrutura foi organizada para que operações que participam do núcleo do cálculo numericamente pesado sejam incorporadas de forma mais direta ao fluxo principal do algoritmo, em vez de depender de múltiplas chamadas em sequência.

### 3. Uso de `do concurrent` como sincronização conceitual

Embora `do concurrent` não seja, em si, uma barreira explícita como `!$omp barrier`, ele introduz uma semântica de independência de iteração que substitui e reorganiza a sincronização do algoritmo. Em vários pontos, a estrutura dos loops foi rearranjada para que o processamento de blocos e fronteiras siga uma ordem em que a concorrência por iteração é segura e as dependências entre regiões de memória ficam bem separadas.

### 4. Suporte a execução em CPU e GPU

A configuração do projeto apresenta duas linhas de compilação:

- CPU: compilação com `nvfortran` e `-stdpar=multicore` e flags como `-O3 -march=native` e `-Minfo=stdpar`
- GPU: compilação com `nvfortran` e `-stdpar=gpu`, incluindo flags específicas de aceleração, como `-Minfo=stdpar` e `-gpu=cc70,fastmath,loadcache:L1,unroll,fma`

A versão GPU é definida em `config/makeGPU.def`, enquanto a versão CPU é definida em `config/makeCPU.def` e em templates de configuração em `config/make.def.template`.

Essa separação permite que o mesmo conjunto de benchmarks seja compilado para ambientes de alta performance baseados em CPU, bem como para GPUs NVIDIA compatíveis com a infraestrutura `stdpar` da linguagem Fortran.

## Estrutura de configuração

Os arquivos em `config/` centralizam o ambiente de compilação e os parâmetros do benchmark.

### Arquivos relevantes

- `config/make.def` — configuração ativa do ambiente
- `config/makeCPU.def` — flags e compiladores para execução em CPU
- `config/makeGPU.def` — flags e compiladores para execução em GPU
- `config/suite.def` — definição dos benchmarks e classes de execução

### Função das flags de compilação

A escolha das flags é o ponto central para adaptar o benchmark ao alvo de execução. O conjunto de opções em `config/makeCPU.def` e `config/makeGPU.def` define não apenas o compilador, mas também o modelo de paralelização, o nível de otimização e a arquitetura alvo.

#### CPU: modelo `do concurrent` em multicore

```make
FC = nvfortran
FFLAGS = -O3 -march=native -stdpar=multicore -Minfo=stdpar
CFLAGS = -O3
```

Cada flag tem um papel específico:

- `FC = nvfortran`: define o compilador Fortran usado para compilar os kernels do benchmark.
- `-O3`: ativa otimização de nível alto, melhorando a geração de código para loops intensivos em computação.
- `-march=native`: direciona o compilador para otimizar o código para a arquitetura local do host, aproveitando instruções específicas do processador.
- `-stdpar=multicore`: instruí o compilador a paralelizar laços `do concurrent` em múltiplos núcleos do CPU, seguindo o modelo `stdpar` de execução em multicore.
- `-Minfo=stdpar`: exibe diagnósticos sobre como os laços foram transformados e paralelizados pelo compilador.
- `CFLAGS = -O3`: aplica otimização equivalente aos programas em C, como IS e DC, sem ativar paralelização explícita em OpenMP.

Esse modo permite a execução paralela do `do concurrent` em CPU via `stdpar`, que permite que o compilador gere código multithread para o host mantendo a mesma estrutura do programa.

#### GPU: modelo `do concurrent` para GPU NVIDIA

```make
FC = nvfortran
FFLAGS = -O3 -stdpar=gpu -Minfo=stdpar -gpu=cc70,fastmath,loadcache:L1,unroll,fma
```

As flags principais têm as seguintes funções:

- `FC = nvfortran`: usa o compilador NVIDIA Fortran, que inclui suporte a `do concurrent` e a geração de código para GPU.
- `-O3`: habilita otimização agressiva do código gerado.
- `-stdpar=gpu`: instruí o compilador a transformar laços `do concurrent` em paralelismo de GPU, seguindo o modelo `stdpar` da linguagem Fortran.
- `-Minfo=stdpar`: imprime mensagens de diagnóstico sobre como a compilação `stdpar` foi aplicada, ajudando a verificar se os laços foram parallelizados e como o compilador interpretou o código.
- `-gpu=cc70`: define a arquitetura alvo da GPU, no caso uma NVIDIA com capacidade compute capability 7.0.
- `fastmath`: permite otimizações matemáticas mais agressivas, acelerando funções transcendentes e operações de ponto flutuante quando a precisão aceita a aproximação.
- `loadcache:L1`: otimiza o uso de cache L1 para melhorar a reutilização de dados e reduzir latência de memória.
- `unroll`: tenta expandir loops para reduzir overhead de controle e melhorar o aproveitamento de pipeline.
- `fma`: habilita operações de multiply-accumulate combinadas, o que melhora eficiência em kernels numéricos.

Essas configurações permitem adaptar a compilação para o ambiente alvo — CPU multiprocessada ou GPU NVIDIA — sem modificar a estrutura lógica dos benchmarks, preservando a mesma implementação numérica e ajustando apenas a forma de execução paralela.

## Scripts de automação de jobs

A automação do fluxo de execução foi organizada em scripts dentro de `bin/`.

### `bin/run_sp_loop.sh`

Este script executa múltiplas rodadas do benchmark SP em CPU usando Slurm. Ele:

- recebe a classe do problema,
- define o número de execuções,
- informa a quantidade de cores,
- dispara a execução do binário em um ambiente de cluster,
- coleta os logs de cada execução,
- consolida os dados em um único arquivo,
- gera um resumo estatístico via `parse_sp_simple.py`.

### `bin/run_sp_loopGPU.sh`

A versão GPU usa o mesmo esquema de repetição, porém direcionado ao ambiente acelerado. Ele:

- executa o binário SP compilado para GPU,
- requisita uma GPU via Slurm,
- salva cada rodada em logs independentes,
- consolida os resultados em uma estrutura de saída por classe e configuração.

### `bin/parse_sp_simple.py`

Este script processa os logs e extrai métricas-chave do benchmark, como:

- `total`
- `rhs`
- `xsolve`
- `ysolve`
- `zsolve`

Ele calcula média e desvio padrão entre diversas execuções e gera um arquivo `summary.txt` com os resultados agregados.

## Diferença em relação à versão original OpenMP

A versão original do NPB em OpenMP usa a paralelização de laços mais diretamente com diretivas como `!$omp parallel do` e sincronização explícita via `barrier`/`nowait`. A versão `stdpar`/`do concurrent` altera a forma como a concorrência é expressa:

- reduz a dependência de diretivas explícitas de OpenMP;
- favorece a inferência de paralelismo pelo compilador;
- reorganiza a estrutura dos kernels para que cada iteração seja independente;
- torna o código mais natural para compilação em arquiteturas heterogêneas.

Em termos práticos, a intenção da adaptação não foi apenas trocar uma sintaxe por outra, mas repensar o benchmark para operar adequadamente em um modelo de execução moderno, com foco em desempenho, portabilidade e uso de aceleração.

## Compilação e execução

A compilação é conduzida com o make do benchmark específico, usando a configuração adequada em `config/`.

Exemplo de compilação em CPU:

```bash
make clean
make sp CLASS = A
```

Com configuração de CPU/GPU importada via `config/make.def`.

Exemplo para execução em CPU com automação:

```bash
cd bin
./run_sp_loop.sh S 5 8
```

Exemplo para execução em GPU:

```bash
cd bin
./run_sp_loopGPU.sh S 5
```

## Observações finais

A variante presente neste repositório representa uma adaptação de benchmark clássico para um ambiente moderno de compilação e execução paralela. A combinação de:

- loops `do concurrent`,
- inlining de rotinas,
- sincronização por estrutura de laços em vez de barreiras explícitas,
- scripts de automação de jobs,
- processamento de métricas de tempo,
- e arquivos de configuração especializados para CPU e GPU,

transforma a implementação original em uma base mais adequada para estudos de desempenho, paralelização em Fortran e execução em sistemas heterogêneos.

Este README descreve o estado atual da adaptação e o conjunto de decisões arquiteturais que tornam os benchmarks NPB executáveis e analisáveis em cenários de computação paralela moderna.
