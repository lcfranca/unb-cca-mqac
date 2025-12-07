# Introdução

A pergunta sobre como mercados processam informação atravessa a história do pensamento econômico como questão simultaneamente técnica, epistemológica e filosófica.  Técnica porque demanda modelos formais capazes de capturar a relação entre informação disponível e formação de preços.  Epistemológica porque interroga os limites do conhecimento possível em sistemas descentralizados onde nenhum agente possui visão completa do todo. Filosófica porque implica juízos sobre racionalidade, eficiência e os fundamentos normativos da organização econômica.  Este trabalho situa-se na interseção dessas dimensões, propondo investigação empírica de uma questão teórica fundamental: em que medida a análise fundamentalista estruturada adiciona informação ao processo de precificação de ativos, ou apenas replica conhecimento já incorporado pelo mecanismo de mercado? 

A tradição intelectual que informa esta investigação remonta ao ensaio seminal de @hayekUseKnowledgeSociety1945, onde o sistema de preços é caracterizado como "maravilha" epistêmica — mecanismo de telecomunicação que condensa informações dispersas e tácitas, o "conhecimento das circunstâncias particulares de tempo e lugar", que nenhum agente central poderia reunir. Para Hayek, o mercado resolve problema computacional de complexidade intratável: agregar bilhões de fragmentos de conhecimento local em sinais de preço que coordenam decisões descentralizadas. A intuição hayekiana foi posteriormente formalizada por @famaEfficientCapitalMarkets1970 na Hipótese dos Mercados Eficientes (EMH), segundo a qual os preços refletem toda informação disponível, tornando impossível a obtenção sistemática de retornos anormais através de análise de dados públicos.

Contudo, a elegância teórica da EMH encontra obstáculo lógico identificado por @grossmanImpossibilityInformationallyEfficient1980: se os preços refletissem perfeitamente toda informação, não haveria incentivo para incorrer nos custos de sua coleta e processamento. O paradoxo de Grossman-Stiglitz estabelece que mercados perfeitamente eficientes são impossíveis — algum grau de ineficiência é necessário para compensar o custo da informação e garantir que agentes continuem a produzi-la. Este teorema fundamenta teoricamente a existência da análise fundamentalista: analistas calculam métricas, constroem modelos e emitem recomendações porque esperam ser compensados por esse esforço através de retornos superiores ao mercado. 

Desenvolvimentos recentes oferecem enquadramentos complementares. A Hipótese dos Mercados Adaptativos de @loAdaptiveMarketsHypothesis2004, formalizada em @loAdaptiveMarketsHypothesis2024, reconcilia eficiência e comportamento através de lente evolucionária: mercados não são eficientes *ou* ineficientes, mas *adaptativos*. A eficiência varia ao longo do tempo, dependendo do ambiente competitivo, da densidade de participantes informados, e da disponibilidade de oportunidades de arbitragem.  Métricas fundamentalistas, nessa perspectiva, são estratégias adaptativas que funcionam em certos regimes e desaparecem quando o mercado se adapta a elas.  A economia da complexidade, desenvolvida no Santa Fe Institute por @arthurComplexityEconomy2014 e sintetizada em @arthurComplexityEconomics2021, oferece enquadramento ainda mais radical: mercados são sistemas adaptativos complexos onde agentes heterogêneos com racionalidade limitada interagem em redes, produzindo dinâmicas emergentes não redutíveis a equilíbrio.  Nessa visão, informação não é simplesmente "refletida" nos preços — é criada, disseminada, distorcida e amplificada em processos que podem incluir herding, cascatas informacionais e bolhas. 

A contribuição pós-hayekiana de @colinjaegerEfficientMarketHypothesis2020 elucida tensão metodológica entre tradições: enquanto Hayek concebia preços como sinais dentro de processo dinâmico de competição, onde conhecimento relevante é tácito e processual, a EMH de Fama trata preços como reflexos de informação em equilíbrio, onde conhecimento é proposicional e agregável. O trabalho de @kucharCompetitionSociallyExtended2025 estende a perspectiva hayekiana para ciência cognitiva, propondo que mercados sejam entendidos como redes de cognição socialmente estendida — não apenas mecanismos de alocação, mas sistemas de aprendizado coletivo onde preferências e conhecimento são formados, não apenas revelados. A implicação para análise fundamentalista é profunda: métricas não apenas "medem" fundamentos — participam do processo cognitivo coletivo que forma preços, podendo tornar-se profecias autorrealizáveis ou autofrustrantes. 

A pergunta central que orienta esta investigação pode ser formulada nos seguintes termos: considerando a Petrobras S.A. (PETR4) como caso empírico, em contexto de expansão para novas fronteiras exploratórias e riscos ESG/regulatórios associados, o acréscimo de informação fundamentalista estruturada — operacionalizada através de motor de *scoring* multidimensional — resulta em aumento mensurável da capacidade explicativa sobre retornos?  Formalmente: o $\Delta R^2$ entre modelo de mercado puro (CAPM) e modelo acrescido de métricas fundamentalistas é estatisticamente significativo e economicamente relevante? 

A relevância do caso Petrobras transcende o interesse específico no ativo. Trata-se da maior empresa brasileira por capitalização de mercado, componente dominante do índice Ibovespa, e objeto de cobertura analítica intensa — dezenas de relatórios de *sell-side*, vigilância permanente de mídia especializada, dados públicos abundantes via CVM e B3.  Se algum ativo deveria estar "perfeitamente precificado" no mercado brasileiro, seria este.  Paradoxalmente, a empresa exibe características que podem gerar fricções informacionais: assimetria entre gestão e investidores, complexidade contábil do setor de óleo e gás, interferência estatal recorrente, e — no momento presente — incerteza binária sobre o desfecho da exploração da Margem Equatorial.  A tensão entre alta cobertura analítica e potencial persistência de mispricings torna PETR4 laboratório ideal para testar a contribuição marginal da análise fundamentalista.

Do ponto de vista metodológico, a abordagem proposta operacionaliza conceitos teóricos abstratos em testes empíricos. O motor Q-VAL, desenvolvido como instrumento de análise multidimensional integrando métricas de Valor, Qualidade e Risco, serve como proxy para o "custo da informação" no sentido de Grossman-Stiglitz: representa esforço sistemático de coleta, processamento e síntese de dados fundamentalistas. A comparação entre modelos econométricos progressivos — do CAPM puro ao modelo acrescido do score Q-VAL — permite quantificar o "retorno" desse investimento informacional via variação explicada ($\Delta R^2$).  A análise é complementada por critérios de informação (AIC, BIC) que penalizam complexidade, respondendo à pergunta crucial: o motor de métricas está adicionando sinal ou apenas ruído?

O trabalho estrutura-se em cinco movimentos.  Primeiro, estabelece fundamentos teóricos sobre o sistema de preços como mecanismo informacional, revisando a tradição hayekiana, a EMH, o paradoxo de Grossman-Stiglitz, e desenvolvimentos contemporâneos em mercados adaptativos e economia da complexidade.  Segundo, contextualiza o caso Petrobras no momento presente — a autorização de exploração da Margem Equatorial e suas implicações para valuation.  Terceiro, descreve a metodologia, incluindo o motor Q-VAL, os modelos econométricos comparativos, e as métricas de avaliação informacional. Quarto, apresenta resultados empíricos — estimação CAPM, score de comprabilidade, e análise de contribuição informacional.  Quinto, discute implicações teóricas e práticas, situando os achados no debate sobre eficiência de mercado e o papel da análise fundamentalista.

Os objetivos específicos deste trabalho são:

1. Estimar o custo de capital próprio de PETR4 via CAPM, estabelecendo baseline de explicação por informação de preço;
2. Calcular métricas fundamentalistas organizadas nas dimensões de Valor, Qualidade e Risco;
3. Desenvolver motor de *scoring* Q-VAL integrando as três dimensões em índice sintético;
4.  Quantificar a contribuição informacional marginal das métricas via análise de $\Delta R^2$ e critérios de informação;
5.  Diagnosticar *mispricing* via comparação entre Implied Cost of Capital e custo teórico;
6. Analisar cenários (base, otimista, pessimista) e sensibilidade do score a variações nas premissas;
7. Discutir implicações dos resultados para a teoria de eficiência de mercado e a prática de análise fundamentalista. 

A hipótese subjacente — de que métricas fundamentalistas adicionam informação não plenamente capturada pelo mecanismo de preços — encontra fundamento teórico no paradoxo de Grossman-Stiglitz e sustentação empírica na literatura de anomalias de mercado e prêmios de fatores.  Contudo, a magnitude e persistência dessa contribuição são questões empíricas que dependem do contexto institucional, da densidade de cobertura analítica, e do regime de mercado vigente. O caso Petrobras oferece oportunidade de testar essas proposições em ambiente de alta densidade informacional e incerteza estrutural sobre cenários futuros — combinação que torna particularmente relevante a pergunta sobre o valor marginal da análise fundamentalista sistemática.

# Fundamentos Teóricos

## O Sistema de Preços como Mecanismo Informacional

A compreensão do mercado financeiro como sistema de processamento de informação constitui uma das contribuições mais profundas da teoria econômica do século XX. A tradição intelectual que informa esta perspectiva remonta ao debate sobre cálculo econômico sob o socialismo, travado nas décadas de 1920 e 1930, onde a questão central era se um planejador central poderia, em princípio, replicar a eficiência alocativa de mercados descentralizados.  A resposta negativa, articulada com maior rigor por Friedrich August von Hayek, transcendeu o debate original para estabelecer fundamentos epistemológicos que permanecem centrais à teoria financeira contemporânea. 

### A Contribuição Hayekiana: Conhecimento Disperso e Coordenação

O ensaio seminal de @hayekUseKnowledgeSociety1945 reformula o problema econômico fundamental.  A questão não é, como supunham economistas anteriores, a alocação ótima de recursos *dados* — problema que, em princípio, admite solução técnica via programação linear ou métodos equivalentes. O problema genuíno é a utilização de conhecimento que *não está dado* a ninguém em sua totalidade.  O conhecimento relevante para decisões econômicas encontra-se disperso entre milhões de agentes, cada qual possuindo fragmentos únicos — "conhecimento das circunstâncias particulares de tempo e lugar" — que nenhum mecanismo centralizador poderia reunir. 

Esta dispersão não é acidental, mas constitutiva da realidade econômica.  O comerciante local conhece o estado de seus estoques, as preferências idiossincráticas de seus clientes, as condições de suas instalações.  O transportador conhece capacidades ociosas, rotas alternativas, condições de tráfego.  O especulador conhece rumores, padrões históricos, correlações sutis.  Cada fragmento de conhecimento é tácito, contextual e frequentemente inarticulável — o que Michael Polanyi denominaria posteriormente *tacit knowledge*, distinguindo-o do conhecimento proposicional formalizável.

O sistema de preços emerge, nesta perspectiva, como solução evolutiva para o problema de coordenação sob dispersão informacional. Hayek caracteriza-o como "maravilha" epistêmica:

> "O aspecto mais significativo deste sistema é a economia de conhecimento com que opera, ou quão pouco os participantes individuais precisam saber para tomar a ação correta. Em forma abreviada, por uma espécie de símbolo, apenas a informação mais essencial é transmitida." [@hayekUseKnowledgeSociety1945, p.  527]

O preço funciona como *estatística suficiente* — no sentido técnico do termo — condensando em um único número toda a informação relevante para a decisão marginal. O agente não precisa conhecer as causas que alteraram condições de oferta e demanda em mercados distantes; basta observar a variação de preços para ajustar seu comportamento de modo coordenado com milhões de outros agentes que também respondem ao mesmo sinal. 

### Do Conhecimento Tácito ao Conhecimento Proposicional

A transição da intuição hayekiana para modelos formais de finanças envolve transformação epistemológica significativa. Para Hayek, o conhecimento relevante é fundamentalmente *processual* e *tácito* — emerge no processo competitivo e não pode ser plenamente articulado fora dele. A formalização subsequente, culminando na Hipótese dos Mercados Eficientes, tratou conhecimento como *proposicional* e *agregável* — conjunto de proposições verdadeiras que podem, em princípio, ser listadas e incorporadas a modelos. 

@colinjaegerEfficientMarketHypothesis2020 analisam esta transformação com rigor historiográfico.  A EMH, argumentam, operacionalizou intuições hayekianas em forma testável, mas ao fazê-lo perdeu dimensões essenciais.  Onde Hayek via processo dinâmico de descoberta — competição como procedimento de exploração do desconhecido —, Fama vê equilíbrio estático onde toda informação já foi descoberta e incorporada.  A tensão entre estas concepções não é meramente acadêmica; implica visões distintas sobre a possibilidade e utilidade da análise fundamentalista. 

A implicação para o presente trabalho é direta.  Se conhecimento relevante é proposicional e já incorporado aos preços (Fama), métricas fundamentalistas não deveriam adicionar poder explicativo.  Se conhecimento é processual e parcialmente tácito (Hayek), métricas podem capturar dimensões que o mercado ainda não processou — ou que processa com defasagem, ruído ou viés.

### Mercados como Processadores de Informação

A metáfora computacional oferece enquadramento complementar.  Mercados podem ser entendidos como sistemas distribuídos de processamento de informação, onde agentes individuais funcionam como processadores locais que recebem sinais (preços, notícias, dados), executam algoritmos (heurísticas, modelos, intuições) e produzem outputs (ordens de compra e venda) que, agregados, geram novos sinais para o sistema. 

Esta perspectiva ilumina tanto a potência quanto as limitações do mecanismo de preços. Como sistema de computação distribuída, o mercado pode processar volumes de informação que excederiam a capacidade de qualquer agente central. A redundância — milhões de agentes processando informações parcialmente sobrepostas — confere robustez: erros individuais tendem a se cancelar, e o sinal agregado emerge com ruído reduzido.  O paralelismo permite resposta rápida a novos dados, com ajustes de preço ocorrendo em milissegundos nos mercados contemporâneos. 

Contudo, sistemas distribuídos são vulneráveis a falhas de coordenação. Comportamento de manada (*herding*) pode amplificar ruído em vez de filtrá-lo.  Cascatas informacionais — onde agentes racionalmente ignoram informação privada para seguir o comportamento observado de outros — podem propagar erros sistematicamente. Bolhas especulativas emergem quando o próprio aumento de preços é interpretado como sinal informativo, gerando feedback positivo que desacopla preços de fundamentos. 

A literatura sobre microestrutura de mercados, iniciada por @glostenBidAskSpread1985 e desenvolvida por @kyleInformedSpeculationImperfect1989, formaliza como informação é incorporada aos preços através do processo de negociação. O *spread* bid-ask reflete, em parte, o custo que formadores de mercado incorrem ao negociar com agentes potencialmente informados. A velocidade de incorporação de informação depende da liquidez, da densidade de participantes informados, e da estrutura do mercado.  Estas fricções microestruturais implicam que a incorporação de informação é processo gradual, não instantâneo — abrindo espaço para que análise fundamentalista capture informação ainda não plenamente refletida nos preços.

---

## Eficiência de Mercado: Da EMH aos Mercados Adaptativos

### A Hipótese dos Mercados Eficientes: Formulação e Taxonomia

A formalização da intuição hayekiana em teoria testável deve-se primordialmente a Eugene Fama, cuja tese de doutorado e trabalhos subsequentes estabeleceram o paradigma dominante em finanças acadêmicas por décadas. A Hipótese dos Mercados Eficientes, articulada em @famaEfficientCapitalMarkets1970, postula que preços de ativos refletem toda informação relevante disponível, tornando impossível a obtenção sistemática de retornos anormais — retornos superiores ao que seria justificado pelo risco assumido. 

Formalmente, um mercado é eficiente com respeito a um conjunto de informações $\Phi_t$ se é impossível obter lucros econômicos negociando com base em $\Phi_t$. Isto implica que:

$$E[R_{t+1} | \Phi_t] = E[R_{t+1}]$$

onde $R_{t+1}$ denota o retorno do ativo no período seguinte. A expectativa condicional ao conjunto de informações iguala a expectativa incondicional — conhecer $\Phi_t$ não permite previsão superior à que seria obtida ignorando essa informação. 

Fama propôs taxonomia tripartite baseada na amplitude do conjunto informacional:

**Eficiência na Forma Fraca:** O conjunto $\Phi_t$ inclui apenas o histórico de preços e retornos passados. Eficiência nesta forma implica que análise técnica — estratégias baseadas em padrões de preços históricos — não pode gerar retornos anormais sistematicamente.  Padrões como "cabeça e ombros", médias móveis ou indicadores de momentum não teriam poder preditivo além do acaso.

**Eficiência na Forma Semi-Forte:** O conjunto $\Phi_t$ inclui toda informação publicamente disponível — demonstrações financeiras, comunicados ao mercado, dados macroeconômicos, notícias. Eficiência nesta forma implica que análise fundamentalista — estratégias baseadas em avaliação de fundamentos econômicos — não pode gerar retornos anormais.  Múltiplos como P/L, P/VP, EV/EBITDA, ou métricas de qualidade como ROE e ROIC, sendo públicos, já estariam incorporados aos preços.

**Eficiência na Forma Forte:** O conjunto $\Phi_t$ inclui toda informação, pública e privada.  Eficiência nesta forma implica que nem mesmo *insiders* com acesso privilegiado poderiam obter retornos anormais. Esta forma é geralmente rejeitada empiricamente, dado que estudos documentam retornos anormais em negociações de insiders [@jaaborImpactInsiderTrading2004]. 

### Evidência Empírica: Anomalias e Prêmios de Fatores

A elegância teórica da EMH confrontou-se, desde o início, com evidência empírica de anomalias — padrões de retorno aparentemente previsíveis que persistem ao longo do tempo e através de mercados. O programa de pesquisa em anomalias de mercado constitui um dos mais extensos da literatura financeira, documentando centenas de variáveis com aparente poder preditivo sobre retornos. 

@fama1998MarketEfficiencyLongterm oferece defesa sofisticada da EMH frente às anomalias. Argumenta que aparentes retornos anormais frequentemente (i) desaparecem quando custos de transação realistas são considerados, (ii) são artefatos de *data snooping* — pesquisadores testando múltiplas hipóteses até encontrar significância estatística —, ou (iii) representam compensação por risco não capturado pelo modelo de precificação utilizado.

O terceiro argumento é particularmente relevante para o presente trabalho. Se o CAPM unifatorial é especificação incompleta — se existem fatores de risco sistemático além do mercado —, então o que parece "alfa" (retorno anormal) pode ser apenas "beta" (compensação por risco) em dimensão não modelada. Esta lógica motivou a extensão do CAPM para modelos multifatoriais. 

@famaCommonRiskFactors1993 propuseram modelo trifatorial, adicionando ao fator de mercado dois fatores empiricamente motivados: SMB (*Small Minus Big*), capturando o prêmio de tamanho — empresas pequenas tendem a gerar retornos superiores —, e HML (*High Minus Low*), capturando o prêmio de valor — empresas com alto índice book-to-market tendem a superar aquelas com baixo índice. O modelo explica parcela substancial da variação transversal de retornos que o CAPM deixava inexplicada. 

Extensões subsequentes adicionaram fatores de momentum [@jegadeeshReturnsBuyingWinners1993], lucratividade e investimento [@famaFivefactorAssetPricing2015], e qualidade [@asnessSizeValueQuality2014]. O modelo de cinco fatores de Fama-French representa, atualmente, especificação padrão para controle de risco em estudos de anomalias:

$$R_{i,t} - R_{f,t} = \alpha_i + \beta_{i,MKT}(R_{m,t} - R_{f,t}) + \beta_{i,SMB}SMB_t + \beta_{i,HML}HML_t + \beta_{i,RMW}RMW_t + \beta_{i,CMA}CMA_t + \varepsilon_{i,t}$$

onde $RMW$ (*Robust Minus Weak*) captura o prêmio de lucratividade e $CMA$ (*Conservative Minus Aggressive*) captura o prêmio de conservadorismo em investimentos. 

A proliferação de fatores gerou preocupação com *overfitting*. @harveyReplicationCrossSection2016 documentam mais de 300 fatores publicados na literatura acadêmica — o "zoológico de fatores" — e argumentam que a maioria representa artefatos estatísticos.  Propõem ajuste de múltiplos testes via controle de *false discovery rate*, elevando substancialmente o limiar para significância estatística. 

### A Hipótese dos Mercados Adaptativos

A tensão entre eficiência teórica e anomalias empíricas motivou formulações alternativas.  A contribuição mais influente é a Hipótese dos Mercados Adaptativos (AMH), proposta por @loAdaptiveMarketsHypothesis2004 e formalizada extensivamente em @loAdaptiveMarketsHypothesis2024.

A AMH reconcilia eficiência e comportamento através de lente evolucionária.  Mercados não são eficientes *ou* ineficientes de modo binário e atemporal; são *adaptativos*, exibindo graus variáveis de eficiência dependendo do ambiente competitivo, da densidade de participantes, e da disponibilidade de oportunidades de arbitragem. A metáfora central é ecológica: mercados são ecossistemas onde "espécies" de estratégias competem por recursos (retornos), com populações expandindo quando estratégias são lucrativas e contraindo quando deixam de sê-lo.

Formalmente, Lo propõe que agentes econômicos comportam-se de acordo com princípios evolucionários: agem em interesse próprio, cometem erros, aprendem e se adaptam, competem por recursos, e estão sujeitos a seleção natural. Estas premissas substituem as do *homo economicus* neoclássico — racionalidade perfeita, informação completa, preferências estáveis — por descrição mais consonante com evidência de psicologia cognitiva e neurociência. 

As implicações diferem substancialmente da EMH:

**Eficiência é contexto-dependente:** Em mercados líquidos com alta densidade de participantes sofisticados (ações de grande capitalização em bolsas desenvolvidas), eficiência tende a ser elevada. Em mercados ilíquidos com poucos participantes (small caps em mercados emergentes, ativos alternativos), ineficiências podem persistir.

**Prêmios de risco variam no tempo:** A compensação exigida por diferentes tipos de risco flutua com condições de mercado, densidade de capital alocado à estratégia, e memória recente de eventos extremos. O prêmio de valor, por exemplo, pode ser elevado em períodos de aversão ao risco e comprimido quando capital abundante persegue a estratégia.

**Estratégias têm "meia-vida":** Anomalias descobertas tendem a desaparecer conforme participantes ajustam comportamento em resposta à informação. A publicação acadêmica de uma anomalia pode, paradoxalmente, eliminar sua lucratividade — fenômeno documentado por @mcleanDoesAcademicResearch2016.

**Inovação cria novas oportunidades:** Mudanças estruturais — novos instrumentos, novas tecnologias, novos regulamentos — criam nichos ecológicos onde ineficiências temporárias emergem antes que o mercado se adapte. 

@hirshleifer2023SocialContagion estendem a análise para incluir dinâmicas de contágio social.  Demonstram que vieses comportamentais não necessariamente desaparecem sob pressão competitiva; podem, ao contrário, persistir e até se amplificar quando transmitidos socialmente. A diversidade de estilos de investimento — valor, crescimento, momentum, qualidade — coexiste porque diferentes estratégias exploram nichos distintos, com desempenho relativo variando ciclicamente.

### Implicações para Análise Fundamentalista

A transição da EMH para a AMH altera substantivamente as expectativas sobre análise fundamentalista.  Sob a EMH estrita (forma semi-forte), métricas fundamentalistas públicas não deveriam ter poder preditivo — se P/L baixo previsse retornos superiores, arbitradores comprariam ações baratas até eliminar o spread.  A persistência do *value premium* por décadas representaria, nesta visão, compensação por risco não modelado.

Sob a AMH, métricas fundamentalistas podem ter poder preditivo variável:

- Em certos regimes (recessões, crises de crédito), quando aversão ao risco é elevada e capital é escasso, o prêmio de valor pode ser substancial.
- Em outros regimes (expansões, abundância de liquidez), quando capital abundante persegue a estratégia, o prêmio pode comprimir-se ou inverter-se. 
- A descoberta e popularização de uma métrica (via publicação acadêmica ou adoção por gestores quantitativos) pode erodir sua eficácia. 

O motor Q-VAL, neste enquadramento, não é tentativa de arbitrar ineficiência permanente, mas instrumento para capturar ineficiência transitória — explorando, no jargão ecológico, nicho que pode existir no mercado brasileiro de ações em determinado regime.  A análise empírica subsequente deve, portanto, considerar não apenas o poder preditivo médio, mas sua variação ao longo do período amostral.

---

## O Paradoxo de Grossman-Stiglitz e o Custo da Informação

### O Teorema de Impossibilidade

Se a EMH fosse literalmente verdadeira — se preços refletissem instantânea e perfeitamente toda informação disponível —, um paradoxo lógico emergiria.  A incorporação de informação aos preços não é processo espontâneo; requer que agentes incorram em custos para coletar, processar e agir sobre informação.  Analistas fundamentalistas dedicam recursos substanciais a examinar demonstrações financeiras, conduzir due diligence, e construir modelos de valuation.  Gestores quantitativos investem em infraestrutura computacional, bases de dados, e talento técnico.  Se toda essa informação já estivesse refletida nos preços, tais investimentos seriam desperdício — seus retornos seriam nulos.

Mas se ninguém investisse em coleta de informação — racionalmente antecipando retornos nulos —, como a informação seria incorporada aos preços? O paradoxo foi formalizado por @grossmanImpossibilityInformationallyEfficient1980 em teorema que permanece central à teoria financeira:

> "Como não poderia haver lucros na coleta de informação, deveria haver pouco motivo para negociar e pouco motivo para que mercados existissem.  Demonstramos que quando a obtenção de informação é custosa, os preços não podem refletir perfeitamente a informação disponível, pois se assim fosse, aqueles que gastaram recursos para obtê-la não receberiam compensação." [@grossmanImpossibilityInformationallyEfficient1980, p. 405]

O teorema estabelece que mercados perfeitamente eficientes são logicamente impossíveis quando informação é custosa. Algum grau de ineficiência — algum retorno anormal para agentes informados — é necessário para compensar o custo da informação e garantir que o processo de incorporação continue operando.

### Formalização: Equilíbrio com Ruído

Grossman e Stiglitz formalizam o argumento em modelo de equilíbrio com dois tipos de agentes: informados (que incorreram no custo $c$ para adquirir informação) e desinformados (que observam apenas o preço).  Em equilíbrio, a fração de agentes informados ajusta-se de modo que o retorno esperado de se tornar informado — o alfa esperado — iguale exatamente o custo da informação. 

Se o preço fosse perfeitamente revelador — se agentes desinformados pudessem inferir toda a informação privada observando o preço —, não haveria vantagem em pagar o custo $c$. A fração de informados cairia a zero.  Mas com zero informados, o preço não conteria informação alguma, tornando vantajoso pagar $c$. A dinâmica oscilaria indefinidamente. 

A solução requer que o preço seja apenas *parcialmente* revelador.  Isto é obtido pela introdução de *noise traders* — agentes cujas demandas são independentes de informação, motivadas por necessidades de liquidez, rebalanceamento, ou irracionalidade. O ruído que estes agentes introduzem impede que o preço revele perfeitamente a informação privada, preservando incentivo para sua aquisição.

Em equilíbrio, a utilidade esperada de agentes informados e desinformados iguala-se.  A fração de informados $\lambda^*$ satisfaz:

$$E[U(W | \text{informado})] - c = E[U(W | \text{desinformado})]$$

O grau de ineficiência — a magnitude do alfa esperado para informados — é função crescente do custo da informação $c$ e decrescente da precisão com que preços revelam informação. 

### Extensões Contemporâneas e Evidência Empírica

A literatura subsequente estendeu o paradigma Grossman-Stiglitz em múltiplas direções.  @verrecchiaInformationAcquisitionCapital1982 endogeniza a quantidade de informação adquirida, mostrando que agentes investem em precisão até o ponto onde benefício marginal iguala custo marginal. @hellwigAggregatingInformationPredict2009 estende a análise para mercados com múltiplos ativos e informação heterogênea, demonstrando condições sob as quais a agregação de informação é mais ou menos eficiente. 

@stiglitzKosenkoEconomicsInformation2024 oferecem atualização abrangente do paradigma da economia da informação.  Argumentam que desenvolvimentos nas décadas desde o trabalho original reforçam, mais que enfraquecem, a centralidade das fricções informacionais. A revolução digital não eliminou assimetrias de informação; em muitos casos, exacerbou-as, criando novas formas de informação privada (dados alternativos, *high-frequency trading*) e novas fontes de ruído (desinformação, manipulação algorítmica).

@pastushkovEvolutionaryModelFinancial2024 aplicam modelagem evolucionária ao problema.  Demonstram resultado contra-intuitivo: reduzir custos de informação não necessariamente aumenta eficiência de preços. Quando informação se torna muito barata, a vantagem competitiva de ser informado diminui, potencialmente levando a equilíbrio onde a maioria permanece desinformada — *free-riding* na informação produzida por poucos.  Apenas quando custos são moderados observa-se equilíbrio com fração substancial de informados e preços relativamente eficientes. 

A evidência empírica oferece suporte misto ao paradigma.  Por um lado, a existência de fundos de investimento ativamente gerenciados — que cobram taxas substanciais para produzir análise — sugere que investidores acreditam haver valor na informação. Por outro lado, a maioria dos fundos ativos não supera benchmarks passivos após taxas [@gruberAnotherPuzzleGrowth1996], sugerindo que a competição por alfa é intensa e que a maior parte do retorno à informação é capturada pelos próprios analistas, não pelos investidores finais.

### O Motor Q-VAL como "Custo da Informação"

O paradoxo de Grossman-Stiglitz fornece enquadramento teórico direto para o presente trabalho. O motor Q-VAL — sistema de scoring que integra métricas de Valor, Qualidade e Risco — representa investimento em informação: coleta de dados fundamentalistas, processamento via algoritmos de normalização e agregação, e síntese em sinal acionável. 

A pergunta empírica pode ser reformulada em termos do teorema: o "alfa" gerado pelo motor Q-VAL — medido via $\Delta R^2$ em relação ao modelo de mercado puro — é suficiente para compensar o "custo" de sua produção? Se $\Delta R^2$ for insignificante, o mercado brasileiro aproxima-se da eficiência semi-forte; métricas fundamentalistas públicas já estariam incorporadas aos preços.  Se $\Delta R^2$ for positivo e significativo, existe espaço para que análise fundamentalista adicione valor — o grau de ineficiência é suficiente para compensar custos informacionais. 

A magnitude do $\Delta R^2$ pode ser interpretada como proxy para o "grau de ineficiência" do mercado brasileiro com respeito a informação fundamentalista. Valores elevados sugeririam que o mercado processa lentamente — ou com viés sistemático — informação contábil pública. Valores baixos sugeririam processamento eficiente.  A análise por subperíodos pode revelar variação temporal — consistente com a AMH — onde ineficiências são maiores em certos regimes (crises, alta volatilidade) e menores em outros. 

---

## Economia da Complexidade e Agregação Informacional

### Mercados como Sistemas Adaptativos Complexos

A economia da complexidade oferece enquadramento radicalmente distinto tanto da visão hayekiana quanto da EMH. Desenvolvida primordialmente no Santa Fe Institute, com contribuições seminais de @arthurComplexityEconomy2014 e sintetizada em @arthurComplexityEconomics2021, esta tradição rejeita a metáfora do mercado como mecanismo de equilíbrio — seja este estático (EMH) ou dinâmico-convergente (Hayek) — em favor da metáfora do mercado como *sistema adaptativo complexo*.

Sistemas adaptativos complexos exibem propriedades que os distinguem tanto de sistemas mecânicos simples quanto de sistemas aleatórios puros:

**Emergência:** Padrões macroscópicos emergem de interações microscópicas de modo não trivialmente dedutível das regras locais. O preço de uma ação emerge de milhões de decisões individuais de compra e venda, mas não pode ser previsto conhecendo-se apenas as regras que governam cada decisão isolada.

**Auto-organização:** Estruturas ordenadas surgem espontaneamente sem coordenação central.  Mercados desenvolvem convenções, normas, instituições — desde horários de negociação até práticas contábeis — sem designer explícito.

**Não-linearidade:** Pequenas perturbações podem gerar efeitos desproporcionais (sensibilidade às condições iniciais), enquanto grandes perturbações podem ser absorvidas sem consequência. O colapso do Lehman Brothers — evento relativamente pequeno no contexto do sistema financeiro global — desencadeou crise sistêmica; outros eventos comparáveis passaram sem repercussão.

**Adaptação:** Agentes modificam comportamento em resposta ao ambiente, e o ambiente modifica-se em resposta ao comportamento agregado.  Estratégias que funcionam atraem imitadores; a imitação altera o ambiente; estratégias que funcionavam deixam de funcionar. 

**Path dependence:** A história importa.  O estado atual do sistema depende não apenas de parâmetros correntes, mas da trajetória pela qual foi atingido. Mercados não "esqueceram" a crise de 2008; participantes, reguladores e instituições foram permanentemente alterados. 

### Agregação de Informação como Fenômeno Emergente

A perspectiva da complexidade reconceptualiza a agregação de informação.  Na visão hayekiana clássica, preços *condensam* informação dispersa, servindo como estatísticas suficientes que permitem coordenação. Na EMH, preços *refletem* informação, igualando-se ao valor esperado condicional a toda informação disponível.  Na economia da complexidade, preços *emergem* de interações que podem tanto agregar quanto distorcer informação. 

@arthurBoundedRationalityElArol1994 desenvolvem modelo seminal — o Bar Problem — demonstrando como agentes com racionalidade limitada, usando heurísticas heterogêneas, podem atingir coordenação eficiente em média, mas com flutuações persistentes que não convergem a equilíbrio.  Aplicado a mercados, o modelo sugere que preços oscilam perpetuamente em torno de "valor fundamental" sem jamais estabilizar — não por choques exógenos, mas por dinâmica endógena do sistema.

O modelo de mercado artificial do Santa Fe Institute [@leBaron2006AgentBasedComputational] simula mercados com agentes heterogêneos que usam regras de decisão evolucionárias.  Os resultados reproduzem "fatos estilizados" observados em mercados reais — caudas gordas nas distribuições de retornos, volatilidade clustering, correlação serial de volatilidade — que modelos de equilíbrio não capturam. Crucialmente, a eficiência informacional do mercado simulado varia: em certos parâmetros, preços rastreiam fundamentos eficientemente; em outros, bolhas e crashes emergem endogenamente.

### Herding, Cascatas e Amplificação de Ruído

A economia da complexidade enfatiza mecanismos pelos quais informação pode ser sistematicamente distorcida — não apenas agregada — pelo mecanismo de mercado. 

**Herding (comportamento de manada):** Agentes podem racionalmente ignorar informação privada para seguir o comportamento observado de outros. Se muitos agentes precedentes compraram um ativo, o agente seguinte pode inferir que eles possuíam informação favorável, e comprar mesmo que sua própria informação seja desfavorável.  O resultado é cascata informacional onde informação privada é perdida e o grupo converge para decisão potencialmente errada [@bikhchandaniTheoryFadsCustom1992].

**Feedback positivo:** Se o aumento de preço de um ativo atrai compradores adicionais — seja porque interpretam o aumento como sinal informativo, seja porque regras de momentum assim ditam —, o próprio movimento de preço gera demanda adicional, desacoplando preços de fundamentos. Bolhas especulativas são manifestação extrema deste mecanismo. 

**Reflexividade:** Conceito desenvolvido por @sorosAlchemyFinance1987, a reflexividade descreve o fenômeno pelo qual expectativas afetam a realidade que pretendem prever. Se analistas acreditam que uma empresa é sólida, concedem crédito a termos favoráveis, atraem talentos, geram cobertura positiva — tornando a empresa efetivamente mais sólida.  Preços não apenas refletem fundamentos; influenciam-nos. 

**Contágio informacional:** Informação — e desinformação — propaga-se através de redes sociais de modo que pode amplificar certos sinais e suprimir outros. @shimirovichSocialMediaStock2011 documentam correlação entre sentimento em redes sociais e retornos subsequentes, sugerindo que "informação" incorporada a preços pode incluir ruído social sistematicamente enviesado.

### Implicações para o Motor Q-VAL

A perspectiva da complexidade sugere cautela interpretativa quanto aos resultados do motor Q-VAL. 

**Regime-dependência:** O poder preditivo de métricas fundamentalistas pode variar substancialmente entre regimes de mercado. Em períodos de baixa volatilidade e liquidez abundante, quando capital busca ativamente oportunidades, ineficiências tendem a ser rapidamente arbitradas. Em períodos de crise, quando aversão ao risco domina e capital foge para ativos seguros, ineficiências podem ampliar-se — ativos subavaliados podem tornar-se mais subavaliados antes de reverter. 

**Reflexividade das métricas:** Se o score Q-VAL — ou métricas similares — for amplamente adotado, sua própria utilização afetará os preços que pretende prever. Empresas que recebem scores elevados atraem fluxo de investimento, elevando preços até que a "oportunidade" desapareça.  Há risco de *self-defeating prophecy* — métricas que funcionam deixam de funcionar justamente porque funcionam.

**Ruído vs. sinal:** A economia da complexidade alerta que nem toda informação incorporada a preços é "informação" no sentido de conhecimento verdadeiro sobre fundamentos. Parte é ruído — flutuações aleatórias, comportamento de manada, cascatas informacionais.  O aumento de $R^2$ observado pode refletir captura de padrões de ruído correlacionado, não genuína informação sobre valor fundamental.

**Não-linearidade:** Modelos lineares — como as regressões propostas na metodologia — podem capturar apenas parcela das relações.  Interações não-lineares entre métricas, efeitos de limiar (*threshold effects*), e dinâmicas de feedback podem requerer especificações mais flexíveis.  A literatura recente em machine learning para precificação de ativos [@guEmpiricalAssetPricing2020] documenta ganhos substanciais com métodos não-lineares, sugerindo que especificações lineares subestimam o conteúdo informacional de métricas fundamentalistas.

### Síntese: Quatro Visões sobre Informação e Preços

O arcabouço teórico desenvolvido nesta seção pode ser sintetizado contrastando quatro visões sobre a relação entre informação e preços:

| Tradição | Metáfora Central | Implicação para Análise Fundamentalista |
|----------|------------------|----------------------------------------|
| **Hayek** | Mercado como telecomunicação | Preços condensam conhecimento tácito; análise pode antecipar processamento |
| **Fama (EMH)** | Mercado como espelho | Preços refletem informação; análise de dados públicos é inútil |
| **Grossman-Stiglitz** | Mercado como incentivo | Ineficiência necessária; análise é compensada por alfa |
| **Complexidade** | Mercado como ecossistema | Eficiência variável; análise funciona em certos nichos/regimes |

Estas visões não são mutuamente exclusivas.  A EMH pode aproximar-se da verdade para ativos líquidos em mercados desenvolvidos, enquanto a economia da complexidade melhor descreve mercados emergentes ou ativos ilíquidos.  O paradoxo de Grossman-Stiglitz opera em todos os contextos, estabelecendo limite inferior para ineficiência.  A intuição hayekiana permanece válida como descrição do *processo* — ainda que o *resultado* possa aproximar-se de eficiência em alguns casos e afastar-se em outros.

Para o caso Petrobras, múltiplas considerações são relevantes.  Por um lado, trata-se de ativo extremamente líquido, com alta cobertura de analistas, sugerindo eficiência elevada. Por outro lado, a empresa está inserida em contexto de mercado emergente, sujeita a interferência estatal, exposta a incerteza estrutural (Margem Equatorial), e caracterizada por complexidade contábil do setor de óleo e gás — fatores que podem gerar fricções informacionais persistentes. 

A análise empírica subsequente buscará distinguir entre estas possibilidades, examinando se o motor Q-VAL adiciona poder explicativo ao modelo de mercado puro, e se este poder explicativo varia ao longo do tempo de modo consistente com a hipótese dos mercados adaptativos.

# Contextualização: Petrobras e a Margem Equatorial

## Trajetória Histórica e Institucional

A Petróleo Brasileiro S.A. — Petrobras — foi constituída em 1953 como instrumento da política desenvolvimentista que marcou o período Vargas. A criação da empresa estatal respondeu a demandas nacionalistas por controle dos recursos petrolíferos, sintetizadas na campanha "O Petróleo é Nosso" que mobilizou segmentos diversos da sociedade brasileira. O monopólio estatal sobre exploração, produção e refino, estabelecido pela Lei 2.004/1953, configurou modelo que prevaleceria por mais de quatro décadas.

A quebra parcial do monopólio em 1997, durante o governo Fernando Henrique Cardoso, inaugurou nova fase. A Emenda Constitucional nº 9/1995 e a Lei do Petróleo (9.478/1997) permitiram a entrada de empresas privadas no setor, embora a Petrobras mantivesse posição dominante. A abertura de capital, com listagem simultânea na B3 e NYSE, introduziu pressões de governança corporativa e transparência típicas de companhias abertas. A empresa passou a operar sob dupla lógica: instrumento de política energética nacional e maximizadora de valor para acionistas.

A descoberta do pré-sal em 2006 representou inflexão histórica. As reservas identificadas na camada de rochas carbonáticas sob espessa camada de sal, em águas ultraprofundas da Bacia de Santos, posicionaram o Brasil entre as principais fronteiras petrolíferas globais. O desenvolvimento do pré-sal exigiu investimentos massivos em tecnologia de perfuração e produção em condições extremas — capacidade que a Petrobras desenvolveu tornando-se referência mundial em águas profundas.

O período subsequente foi marcado por escândalo de corrupção de proporções inéditas. A Operação Lava Jato, deflagrada em 2014, revelou esquema de pagamentos ilícitos envolvendo contratos da Petrobras, partidos políticos e empreiteiras. As consequências foram severas: baixas contábeis bilionárias, rebaixamento de rating de crédito, queda abrupta do valor de mercado, e crise de governança que culminou em renovação completa da alta administração. A recuperação, iniciada a partir de 2016, envolveu desinvestimentos, redução de alavancagem e foco em ativos de maior rentabilidade — notadamente o pré-sal.

## O Cenário Atual: Margem Equatorial e Transição Energética

A Margem Equatorial brasileira compreende as bacias sedimentares da costa norte do país, estendendo-se do Amapá ao Rio Grande do Norte. Trata-se de fronteira exploratória praticamente inexplorada, com potencial estimado entre 10 e 30 bilhões de barris de petróleo — volume que poderia duplicar as reservas provadas brasileiras. A região apresenta características geológicas análogas a províncias produtoras da costa oeste africana, onde descobertas significativas foram realizadas nas últimas décadas.

A autorização para exploração da Margem Equatorial, concedida pelo IBAMA em 2024-2025, reacendeu debates sobre a estratégia de longo prazo da Petrobras. De um lado, a exploração representa oportunidade de expansão de reservas em momento em que campos maduros declinam e o pré-sal, embora produtivo, apresenta horizonte finito. De outro, implica investimentos vultosos — estimados entre US$ 50 e 100 bilhões — com retorno incerto e prazo de maturação superior a uma década.

O contexto de transição energética adiciona camada de complexidade à decisão. O Acordo de Paris e os compromissos subsequentes de neutralidade de carbono pressionam empresas petrolíferas a reorientar portfólios para fontes renováveis. Investidores institucionais, especialmente fundos de pensão europeus e gestores com mandatos ESG, questionam a racionalidade de investimentos em novas fronteiras fósseis. A Petrobras enfrenta, nesse cenário, tensão entre maximização de valor de curto prazo via exploração de reservas e posicionamento estratégico para economia descarbonizada.

Os riscos regulatórios e ambientais da Margem Equatorial são substanciais. A região abriga ecossistemas sensíveis, incluindo manguezais, recifes de coral e áreas de reprodução de espécies marinhas. O licenciamento ambiental tem sido objeto de contestação judicial e mobilização de organizações ambientalistas. Vazamentos ou acidentes em área de difícil acesso teriam consequências potencialmente graves, com repercussões sobre a reputação da empresa e sua licença social para operar.

## Implicações para Valuation

A avaliação da PETR4 no contexto descrito envolve ponderação de cenários com probabilidades e payoffs distintos. No cenário otimista, a exploração da Margem Equatorial confirma potencial geológico, custos de desenvolvimento permanecem controlados, e preços de petróleo sustentam-se em patamares remuneradores. Os fluxos de caixa incrementais justificam o investimento e o valor da empresa aumenta significativamente. No cenário pessimista, reservas mostram-se menores que o esperado, custos escalam além das projeções, preços de petróleo colapsam com aceleração da transição energética, e pressões ESG restringem acesso a capital. Os investimentos tornam-se *stranded assets* e o valor da empresa deteriora-se.

O mercado, ao precificar a PETR4, pondera implicitamente esses cenários. A pergunta relevante para o investidor é se essa ponderação está correta — se o preço corrente reflete adequadamente o valor esperado da empresa considerando probabilidades e magnitudes dos diferentes cenários. A análise de *mispricing* via comparação entre custo de capital implícito e custo de capital teórico (CAPM) oferece uma abordagem para essa questão.

# Metodologia

A metodologia deste trabalho articula três componentes integrados: (i) a construção do motor Q-VAL como sistema de agregação de informação fundamentalista, (ii) a especificação de modelos econométricos comparativos que permitem isolar a contribuição informacional de cada componente, e (iii) a definição de métricas de avaliação que operacionalizam conceitos teóricos — eficiência informacional, contribuição marginal, parcimônia — em quantidades mensuráveis.  A integração destes componentes permite responder à pergunta central: métricas fundamentalistas adicionam informação ao processo de precificação, ou essa informação já está incorporada aos preços? 

A estratégia empírica segue lógica de *nested models* (modelos aninhados), partindo de especificação mínima — o CAPM unifatorial — e progressivamente incorporando vetores de informação fundamentalista. A comparação entre modelos sucessivos, via métricas como $\Delta R^2$ e critérios de informação, permite atribuir a cada componente sua contribuição marginal explicativa. Esta abordagem dialoga diretamente com o paradoxo de Grossman-Stiglitz: se métricas públicas já estão precificadas, sua adição não deveria melhorar o poder explicativo; se existe ineficiência compensadora, a melhoria será estatisticamente detectável.

---

## O Motor Q-VAL como Vetor de Informação Fundamentalista

### Arquitetura Conceitual

O motor Q-VAL (*Quantitative Value*) constitui sistema de *scoring* fundamentalista que integra múltiplas dimensões de avaliação em índice sintético. A denominação remete à tradição de *Quantitative Value Investing* sistematizada por @grayQuantitativeValuePractitioners2012, que propõe automatização de princípios de análise fundamentalista clássica — originários de @grahamSecurityAnalysis1934 — via algoritmos computacionais que eliminam vieses comportamentais e garantem consistência metodológica. 

A arquitetura do motor organiza-se em três dimensões canônicas:

**Dimensão de Valor:** Captura a relação entre preço de mercado e fundamentos contábeis.  Métricas de valor respondem à pergunta: *quanto o mercado está pagando por unidade de fundamento econômico? * Valores baixos (P/L reduzido, EV/EBITDA comprimido) sugerem subavaliação — o mercado atribui ao ativo preço inferior ao que seus fundamentos justificariam.  A literatura documenta *value premium* persistente: ativos "baratos" tendem, em média, a superar ativos "caros" em horizontes de médio prazo [@famaCommonRiskFactors1993; @asnesValueMomentumEverywhere2013].

**Dimensão de Qualidade:** Avalia a eficiência operacional e sustentabilidade dos resultados. Métricas de qualidade respondem à pergunta: *quão eficientemente a empresa converte capital em retorno? * Valores elevados (ROE alto, margens robustas, crescimento consistente) indicam vantagens competitivas que tendem a persistir.  @novy-marxOtherSideValue2013 documenta que lucratividade possui poder preditivo comparável ao de métricas de valor, enquanto @asnessSizeValueQuality2019 formalizam "qualidade" como fator distinto com prêmio próprio.

**Dimensão de Risco:** Incorpora indicadores de alavancagem, liquidez e volatilidade. Métricas de risco respondem à pergunta: *qual a probabilidade de deterioração dos fundamentos ou de eventos adversos?* A inclusão desta dimensão reconhece que ativos "baratos e de qualidade" podem sê-lo por razões legítimas — risco elevado que justifica desconto.  A dimensão de risco serve como *hedge* contra *value traps*: ativos superficialmente atrativos que ocultam fragilidades estruturais.

### Métricas Selecionadas

A seleção de métricas segue critérios de relevância teórica, disponibilidade de dados, e robustez empírica documentada na literatura. Para cada dimensão, escolheu-se conjunto parcimonioso de indicadores que capturam facetas complementares:

#### Dimensão de Valor

| Métrica | Definição | Interpretação |
|---------|-----------|---------------|
| **Earnings Yield (EY)** | $\frac{\text{LPA}}{\text{Preço}} = \frac{1}{\text{P/L}}$ | Retorno implícito do lucro; inverso do P/L |
| **EV/EBITDA** | $\frac{\text{Enterprise Value}}{\text{EBITDA}}$ | Múltiplo de valor da firma sobre geração de caixa operacional |
| **P/VP** | $\frac{\text{Preço}}{\text{Valor Patrimonial por Ação}}$ | Relação entre valor de mercado e valor contábil |
| **Dividend Yield (DY)** | $\frac{\text{Dividendos por Ação}}{\text{Preço}}$ | Retorno em dividendos |

O *Earnings Yield* é preferido ao P/L por conveniência matemática: valores mais altos indicam maior atratividade (inversamente ao P/L), facilitando agregação com outras métricas onde "maior é melhor".  O EV/EBITDA captura valor da firma inteira — incluindo dívida — sobre geração de caixa operacional, sendo particularmente relevante para empresas intensivas em capital como a Petrobras.

#### Dimensão de Qualidade

| Métrica | Definição | Interpretação |
|---------|-----------|---------------|
| **ROIC** | $\frac{\text{NOPAT}}{\text{Capital Investido}}$ | Retorno sobre capital investido |
| **ROE** | $\frac{\text{Lucro Líquido}}{\text{Patrimônio Líquido}}$ | Retorno sobre patrimônio |
| **Margem EBITDA** | $\frac{\text{EBITDA}}{\text{Receita Líquida}}$ | Eficiência operacional |
| **EVS** | $\text{ROIC} - \text{WACC}$ | Economic Value Spread; criação de valor |

O *Economic Value Spread* (EVS) merece destaque.  Conforme desenvolvido na seção de fundamentos teóricos, o EVS captura criação de valor em termos relativos ao custo de capital.  Valor positivo indica que a empresa gera retorno superior ao custo de oportunidade do capital empregado — condição necessária para criação sustentável de valor ao acionista.  Para empresas do setor de óleo e gás, onde ciclos de investimento são longos e intensivos em capital, o EVS oferece perspectiva mais informativa que métricas de rentabilidade brutas.

#### Dimensão de Risco

| Métrica | Definição | Interpretação |
|---------|-----------|---------------|
| **Beta** | $\frac{\text{Cov}(R_i, R_m)}{\text{Var}(R_m)}$ | Sensibilidade ao mercado |
| **Volatilidade** | $\sigma_i = \sqrt{\text{Var}(R_i)}$ | Desvio-padrão dos retornos |
| **Dívida/PL** | $\frac{\text{Dívida Total}}{\text{Patrimônio Líquido}}$ | Alavancagem financeira |
| **Liquidez Corrente** | $\frac{\text{Ativo Circulante}}{\text{Passivo Circulante}}$ | Capacidade de pagamento de curto prazo |

O beta, estimado via regressão conforme detalhado adiante, captura risco sistemático — a parcela do risco que não pode ser eliminada por diversificação. A volatilidade captura risco total.  A razão Dívida/PL indica exposição a risco financeiro — empresas alavancadas são mais sensíveis a choques de receita e taxa de juros. A liquidez corrente sinaliza risco de curto prazo — capacidade de honrar obrigações imediatas.

### Procedimento de Normalização

Métricas heterogêneas — expressas em unidades distintas (percentuais, múltiplos, razões) e com escalas variadas — requerem normalização para agregação. O procedimento adotado é a *padronização Z-Score* relativa a benchmarks setoriais:

$$Z_i = \frac{X_i - \mu_{\text{setor}}}{\sigma_{\text{setor}}}$$

onde $X_i$ é o valor da métrica para o ativo $i$, $\mu_{\text{setor}}$ é a média setorial, e $\sigma_{\text{setor}}$ é o desvio-padrão setorial.  O Z-Score indica quantos desvios-padrão o ativo se afasta da média do setor: $Z = +1$ indica desempenho um desvio-padrão acima da média; $Z = -1$, um desvio abaixo.

Para métricas onde valores *menores* são preferíveis (P/VP, EV/EBITDA, Dívida/PL, Volatilidade, Beta), o Z-Score é invertido:

$$Z_i^{\text{inv}} = -Z_i = \frac{\mu_{\text{setor}} - X_i}{\sigma_{\text{setor}}}$$

Esta inversão garante que, para todas as métricas normalizadas, valores mais altos indicam maior atratividade. 

Os benchmarks setoriais são obtidos de empresas comparáveis do setor de óleo e gás integrado, utilizando dados de empresas listadas na B3 e, quando necessário para robustez estatística, médias de empresas latino-americanas do setor obtidas via bases de dados internacionais. 

### Agregação em Score Composto

Os Z-Scores normalizados são agregados em score composto via média ponderada:

$$\text{Score}_{\text{Dimensão}} = \sum_{j=1}^{n} w_j \cdot Z_j$$

onde $w_j$ são pesos atribuídos a cada métrica dentro da dimensão, com $\sum w_j = 1$. Na implementação base, pesos iguais são atribuídos a cada métrica dentro de cada dimensão ($w_j = 1/n$). 

O score final Q-VAL agrega as três dimensões:

$$\text{Q-VAL} = w_V \cdot \text{Score}_{\text{Valor}} + w_Q \cdot \text{Score}_{\text{Qualidade}} + w_R \cdot \text{Score}_{\text{Risco}}$$

Na configuração base, pesos iguais são atribuídos às dimensões ($w_V = w_Q = w_R = 1/3$).  A análise de sensibilidade examina configurações alternativas. 

Para facilitar interpretação, o score é transformado em escala 0-100:

$$\text{Q-VAL}_{[0,100]} = 50 + 10 \cdot \text{Q-VAL}_{\text{bruto}}$$

Scores acima de 60 indicam recomendação de *Compra*; entre 40 e 60, *Neutro*; abaixo de 40, *Venda*. Estes limiares correspondem aproximadamente a $\pm 1$ desvio-padrão em torno da média. 

### Série Temporal de Scores

Para a análise de contribuição informacional, é necessário construir série temporal de scores. A cada período $t$, o score Q-VAL é calculado utilizando apenas informação disponível até $t$ — critério essencial para evitar *look-ahead bias*.  Formalmente:

$$\text{Q-VAL}_t = f(\mathcal{I}_t)$$

onde $\mathcal{I}_t$ denota o conjunto de informação disponível no período $t$.  Na prática, dados contábeis são defasados: demonstrações financeiras do trimestre $q$ tornam-se públicas apenas semanas após o encerramento do trimestre.  O procedimento utiliza dados do trimestre $q-1$ para calcular scores no trimestre $q$, garantindo que toda informação utilizada era publicamente disponível no momento da decisão. 

---

## Modelos Econométricos Comparativos

### Estratégia de Modelos Aninhados

A estratégia empírica baseia-se em comparação de modelos aninhados (*nested models*), partindo de especificação mínima e progressivamente incorporando regressores. Esta abordagem permite decompor o poder explicativo total em contribuições atribuíveis a cada componente, testando se a adição de variáveis fundamentalistas melhora significativamente a explicação dos retornos. 

Sejam $\mathcal{M}_0, \mathcal{M}_1, \ldots, \mathcal{M}_K$ modelos aninhados, onde $\mathcal{M}_0 \subset \mathcal{M}_1 \subset \ldots \subset \mathcal{M}_K$ (cada modelo contém os regressores do anterior mais regressores adicionais). A comparação entre $\mathcal{M}_k$ e $\mathcal{M}_{k-1}$ permite testar se os regressores adicionais em $\mathcal{M}_k$ contribuem significativamente para explicar a variável dependente. 

### Modelo 0: CAPM (Baseline)

O modelo base é o Capital Asset Pricing Model unifatorial, que representa a informação contida exclusivamente nos preços de mercado:

$$R_{i,t} - R_{f,t} = \alpha_i + \beta_i (R_{m,t} - R_{f,t}) + \varepsilon_{i,t}$$

onde:
- $R_{i,t}$: retorno do ativo $i$ no período $t$
- $R_{f,t}$: taxa livre de risco no período $t$
- $R_{m,t}$: retorno do portfólio de mercado no período $t$
- $\alpha_i$: intercepto (alfa de Jensen)
- $\beta_i$: coeficiente de sensibilidade ao mercado (beta)
- $\varepsilon_{i,t}$: termo de erro, com $E[\varepsilon_{i,t}] = 0$ e $\text{Var}(\varepsilon_{i,t}) = \sigma^2_\varepsilon$

O CAPM postula que $\alpha_i = 0$ em equilíbrio: todo o retorno esperado em excesso é explicado pela exposição ao risco de mercado. Alfa positivo indica retorno anormal — desempenho superior ao previsto pelo modelo dado o nível de risco. 

**Operacionalização:**
- $R_{i,t}$: retorno logarítmico diário de PETR4, calculado como $\ln(P_t / P_{t-1})$
- $R_{f,t}$: taxa CDI diária, obtida via série histórica do Banco Central
- $R_{m,t}$: retorno logarítmico diário do Ibovespa

A estimação utiliza Mínimos Quadrados Ordinários (OLS).  O beta estimado $\hat{\beta}_i$ é dado por:

$$\hat{\beta}_i = \frac{\text{Cov}(R_i - R_f, R_m - R_f)}{\text{Var}(R_m - R_f)}$$

O $R^2$ do Modelo 0 indica a fração da variância dos retornos de PETR4 explicada pelo movimento do mercado. Este valor serve como *baseline* para comparação com modelos subsequentes.

### Modelo 1: CAPM + Fator de Valor

O primeiro modelo estendido adiciona um fator de valor — métrica fundamentalista única — ao CAPM:

$$R_{i,t} - R_{f,t} = \alpha_i + \beta_i (R_{m,t} - R_{f,t}) + \gamma_1 \cdot \text{Value}_{t-1} + \varepsilon_{i,t}$$

onde $\text{Value}_{t-1}$ é o Z-Score da dimensão de Valor no período anterior. O subscrito $t-1$ é crucial: utiliza-se informação fundamentalista *defasada* para prever retorno *corrente*, evitando simultaneidade e garantindo que o modelo é operacionalmente implementável (a informação estava disponível antes do retorno ocorrer).

O coeficiente $\gamma_1$ captura a relação entre posição fundamentalista de valor e retorno subsequente. Valor positivo e significativo indicaria que ativos "baratos" (alto Z-Score de Valor) tendem a gerar retornos superiores — evidência de *value premium* não capturada pelo beta de mercado.

### Modelo 2: CAPM + Três Dimensões Fundamentalistas

O segundo modelo estendido incorpora as três dimensões do Q-VAL separadamente:

$$R_{i,t} - R_{f,t} = \alpha_i + \beta_i (R_{m,t} - R_{f,t}) + \gamma_1 \cdot \text{Value}_{t-1} + \gamma_2 \cdot \text{Quality}_{t-1} + \gamma_3 \cdot \text{Risk}_{t-1} + \varepsilon_{i,t}$$

Esta especificação permite identificar a contribuição marginal de cada dimensão. Os coeficientes $\gamma_1, \gamma_2, \gamma_3$ indicam, respectivamente:
- $\gamma_1 > 0$: ativos baratos tendem a superar após controlar por qualidade e risco
- $\gamma_2 > 0$: ativos de qualidade superior tendem a superar após controlar por valor e risco
- $\gamma_3 > 0$: ativos de menor risco (Z-Score invertido, logo maior Z indica menor risco) tendem a superar após controlar por valor e qualidade

A significância individual de cada coeficiente informa sobre a contribuição de cada dimensão.  A comparação do $R^2$ com o Modelo 1 informa sobre a contribuição conjunta de Qualidade e Risco além de Valor.

### Modelo 3: CAPM + Score Q-VAL Sintético

O terceiro modelo utiliza o score composto Q-VAL como regressor único:

$$R_{i,t} - R_{f,t} = \alpha_i + \beta_i (R_{m,t} - R_{f,t}) + \lambda \cdot \text{Q-VAL}_{t-1} + \varepsilon_{i,t}$$

O coeficiente $\lambda$ captura a relação entre o score agregado e retornos subsequentes. Esta especificação testa se a síntese das três dimensões em índice único preserva (ou potencialmente amplifica) o poder informacional. 

A comparação entre Modelos 2 e 3 é informativa.  Se $R^2_{\text{Modelo 3}} \approx R^2_{\text{Modelo 2}}$, a agregação não perde informação relevante. Se $R^2_{\text{Modelo 3}} < R^2_{\text{Modelo 2}}$, a agregação suprime heterogeneidade informativa entre dimensões.  Se $R^2_{\text{Modelo 3}} > R^2_{\text{Modelo 2}}$, a agregação reduz ruído e amplifica sinal — resultado contra-intuitivo que indicaria overfitting nas dimensões separadas.

### Especificação com Retornos Futuros

Para testar capacidade preditiva — não apenas contemporânea —, especificação alternativa utiliza retorno futuro como variável dependente:

$$R_{i,t+h} - R_{f,t+h} = \alpha_i + \beta_i (R_{m,t+h} - R_{f,t+h}) + \lambda \cdot \text{Q-VAL}_{t} + \varepsilon_{i,t+h}$$

onde $h$ é o horizonte de previsão (1 dia, 5 dias, 21 dias, 63 dias, 252 dias).  Esta especificação testa se informação fundamentalista antecipa retornos futuros — condição necessária para que a análise fundamentalista seja operacionalmente útil para decisões de investimento. 

### Considerações Econométricas

**Heterocedasticidade:** Séries financeiras tipicamente exibem volatilidade variável no tempo (*volatility clustering*).  Erros-padrão robustos à heterocedasticidade (Huber-White) são utilizados para inferência. 

**Autocorrelação:** Retornos diários podem exibir autocorrelação de curto prazo.  Testes de Durbin-Watson e Breusch-Godfrey verificam a presença de autocorrelação residual.  Quando detectada, erros-padrão Newey-West são utilizados.

**Multicolinearidade:** As três dimensões fundamentalistas podem ser correlacionadas. A matriz de correlação entre regressores é examinada, e o *Variance Inflation Factor* (VIF) é calculado.  VIF superior a 5 indicaria multicolinearidade problemática, requerendo ortogonalização ou exclusão de variáveis.

**Estacionariedade:** Séries de retornos são tipicamente estacionárias (retornos são diferenças de log-preços). Testes ADF (*Augmented Dickey-Fuller*) confirmam estacionariedade das séries utilizadas.

**Outliers:** Eventos extremos (crises, circuit breakers) podem distorcer estimativas. Análise de resíduos identifica observações influentes; estimação robusta (regressão quantílica, *winsorização* de extremos) verifica sensibilidade dos resultados.

---

## Métricas de Avaliação Informacional

### Coeficiente de Determinação e Sua Variação

O coeficiente de determinação $R^2$ mede a fração da variância da variável dependente explicada pelo modelo:

$$R^2 = 1 - \frac{\text{SQR}}{\text{SQT}} = 1 - \frac{\sum_{t=1}^{T}(y_t - \hat{y}_t)^2}{\sum_{t=1}^{T}(y_t - \bar{y})^2}$$

onde SQR é a soma dos quadrados dos resíduos e SQT é a soma dos quadrados totais. 

O $R^2$ varia entre 0 (modelo não explica nada além da média) e 1 (modelo explica perfeitamente).  Para modelos de precificação de ativos, valores típicos situam-se entre 0,20 e 0,50 para dados de alta frequência (diários) e podem ser menores para dados de baixa frequência ou para ativos individuais.

**Variação do $R^2$ ($\Delta R^2$):**

A métrica central deste trabalho é a variação do coeficiente de determinação entre modelos aninhados:

$$\Delta R^2_{k} = R^2_{\mathcal{M}_k} - R^2_{\mathcal{M}_{k-1}}$$

Esta quantidade mede a contribuição marginal dos regressores adicionais no modelo $k$ à explicação da variância. 

**Interpretação à luz da teoria:**

| Resultado | Interpretação | Implicação Teórica |
|-----------|---------------|-------------------|
| $\Delta R^2 \approx 0$ | Métricas fundamentalistas não adicionam poder explicativo | Mercado eficiente; informação já precificada (Fama) |
| $\Delta R^2 > 0$, pequeno | Contribuição marginal modesta | Ineficiência limitada; compensação por custo informacional (Grossman-Stiglitz) |
| $\Delta R^2 > 0$, substancial | Contribuição significativa | Ineficiência material; oportunidade para análise fundamentalista |
| $\Delta R^2$ variável no tempo | Contribuição regime-dependente | Mercados adaptativos (Lo) |

### $R^2$ Ajustado

O $R^2$ simples aumenta mecanicamente com a adição de regressores, mesmo que estes não tenham genuíno poder explicativo. O $R^2$ ajustado penaliza a adição de variáveis:

$$R^2_{\text{adj}} = 1 - \frac{(1 - R^2)(n - 1)}{n - k - 1}$$

onde $n$ é o número de observações e $k$ é o número de regressores (excluindo o intercepto). 

A comparação de $R^2_{\text{adj}}$ entre modelos informa se a adição de variáveis melhora genuinamente a explicação ou apenas adiciona complexidade sem benefício.  Se $R^2_{\text{adj, Modelo k}} > R^2_{\text{adj, Modelo k-1}}$, a adição de regressores é justificada.

### Critérios de Informação

Critérios de informação oferecem enquadramento alternativo — e mais rigoroso — para comparação de modelos, penalizando complexidade de modo mais severo que o $R^2$ ajustado. 

**Critério de Informação de Akaike (AIC):**

$$\text{AIC} = 2k - 2\ln(\hat{L})$$

onde $k$ é o número de parâmetros estimados e $\hat{L}$ é a verossimilhança maximizada.  Para modelos de regressão linear com erros gaussianos:

$$\text{AIC} = n \ln\left(\frac{\text{SQR}}{n}\right) + 2k$$

**Critério de Informação Bayesiano (BIC):**

$$\text{BIC} = k \ln(n) - 2\ln(\hat{L})$$

ou, para regressão linear:

$$\text{BIC} = n \ln\left(\frac{\text{SQR}}{n}\right) + k \ln(n)$$

O BIC penaliza complexidade mais severamente que o AIC (o termo $k \ln(n)$ cresce com o tamanho amostral, enquanto $2k$ é constante).  Em amostras grandes, o BIC tende a selecionar modelos mais parcimoniosos. 

**Interpretação:** O modelo preferido é aquele com menor AIC (ou BIC).  A diferença $\Delta \text{AIC} = \text{AIC}_{\mathcal{M}_k} - \text{AIC}_{\mathcal{M}_{k-1}}$ indica se o modelo mais complexo é preferível:
- $\Delta \text{AIC} < 0$: modelo mais complexo é preferível
- $\Delta \text{AIC} > 0$: modelo mais parcimonioso é preferível
- $|\Delta \text{AIC}| < 2$: diferença não é substancial

Regras análogas aplicam-se ao BIC, tipicamente com limiares mais conservadores ($|\Delta \text{BIC}| < 6$).

### Testes de Significância Estatística

**Teste F para Modelos Aninhados:**

O teste F compara formalmente modelos aninhados, testando a hipótese nula de que os coeficientes adicionais são conjuntamente zero:

$$H_0: \gamma_1 = \gamma_2 = \ldots = \gamma_p = 0$$

A estatística de teste é:

$$F = \frac{(R^2_{\mathcal{M}_k} - R^2_{\mathcal{M}_{k-1}}) / p}{(1 - R^2_{\mathcal{M}_k}) / (n - k - 1)}$$

onde $p$ é o número de regressores adicionais. Sob $H_0$, a estatística segue distribuição $F(p, n-k-1)$. Rejeição de $H_0$ indica que os regressores adicionais contribuem significativamente. 

**Teste t para Coeficientes Individuais:**

A significância individual de cada coeficiente é testada via estatística t:

$$t_j = \frac{\hat{\gamma}_j}{\text{SE}(\hat{\gamma}_j)}$$

onde $\text{SE}(\hat{\gamma}_j)$ é o erro-padrão do coeficiente estimado. Sob $H_0: \gamma_j = 0$, a estatística segue distribuição $t(n-k-1)$.  Com erros-padrão robustos, a distribuição assintótica é normal padrão.

### Validação Out-of-Sample

Métricas in-sample — calculadas sobre os mesmos dados usados para estimação — podem superestimar o poder preditivo real, especialmente quando o modelo possui muitos parâmetros relativamente ao tamanho amostral (*overfitting*).  Validação out-of-sample oferece estimativa mais conservadora e operacionalmente relevante.

**Divisão Temporal:**

O período amostral é dividido em:
- **Período de treinamento** (in-sample): Janeiro/2016 a Dezembro/2022 (~7 anos)
- **Período de teste** (out-of-sample): Janeiro/2023 a Novembro/2025 (~3 anos)

Os modelos são estimados no período de treinamento; o poder preditivo é avaliado no período de teste.  O $R^2$ out-of-sample ($R^2_{\text{OOS}}$) é calculado como:

$$R^2_{\text{OOS}} = 1 - \frac{\sum_{t \in \text{teste}}(y_t - \hat{y}_t)^2}{\sum_{t \in \text{teste}}(y_t - \bar{y}_{\text{treino}})^2}$$

Note que a média utilizada no denominador é a média do período de *treinamento*, não do teste — garantindo que nenhuma informação futura contamina a avaliação.

**Validação Cruzada Rolling-Window:**

Para avaliar estabilidade temporal, implementa-se validação cruzada com janelas móveis:

1.  Estima-se o modelo em janela de 252 dias úteis (~1 ano)
2. Prevê-se o retorno do dia seguinte
3.  Desloca-se a janela um dia adiante
4. Repete-se o processo

O $R^2$ rolling é calculado para cada posição da janela, gerando série temporal de poder explicativo.  A variação desta série informa sobre estabilidade — ou regime-dependência — da contribuição informacional das métricas fundamentalistas.

### Métricas Complementares

**Erro Quadrático Médio (MSE) e Raiz do Erro Quadrático Médio (RMSE):**

$$\text{MSE} = \frac{1}{n}\sum_{t=1}^{n}(y_t - \hat{y}_t)^2$$
$$\text{RMSE} = \sqrt{\text{MSE}}$$

O RMSE tem a vantagem de estar na mesma unidade da variável dependente (retorno), facilitando interpretação econômica.

**Erro Absoluto Médio (MAE):**

$$\text{MAE} = \frac{1}{n}\sum_{t=1}^{n}|y_t - \hat{y}_t|$$

O MAE é menos sensível a outliers que o MSE/RMSE. 

**Razão de Sharpe da Estratégia:**

Para avaliar relevância econômica — não apenas estatística — dos resultados, constrói-se estratégia de investimento baseada no score Q-VAL e calcula-se sua razão de Sharpe:

$$\text{Sharpe} = \frac{E[R_{\text{estratégia}}] - R_f}{\sigma_{\text{estratégia}}}$$

A estratégia assume posição *long* quando Q-VAL indica *Compra*, posição *cash* quando indica *Neutro*, e posição *short* (se permitida) ou *cash* quando indica *Venda*. Comparação com estratégia *buy-and-hold* do Ibovespa informa sobre valor agregado operacional.

---

## Fontes de Dados e Período de Análise

### Dados Utilizados

Os dados para este trabalho provêm de três fontes complementares:

**Preços e Retornos:**
- Preços de fechamento ajustados de PETR4 e do índice Ibovespa: API Brapi e B3
- Período: Janeiro/2016 a Novembro/2025
- Frequência: Diária (dias úteis)
- Total aproximado: 2.460 observações

**Dados Fundamentalistas:**
- Demonstrações financeiras trimestrais: CVM (Comissão de Valores Mobiliários)
- Múltiplos e métricas derivadas: API Brapi
- Dados setoriais para benchmarking: bases públicas complementares

**Taxa Livre de Risco:**
- CDI (Certificado de Depósito Interbancário): Banco Central do Brasil
- Frequência: Diária
- Conversão para taxa diária: $(1 + \text{CDI}_{\text{anual}})^{1/252} - 1$

### Tratamento de Dados

**Ajuste de Proventos:** Preços são ajustados para dividendos, juros sobre capital próprio, bonificações e desdobramentos, garantindo comparabilidade temporal. 

**Dados Faltantes:** Observações com dados faltantes são tratadas via:
- Interpolação linear para lacunas curtas (< 5 dias)
- Exclusão para lacunas longas
- Forward-fill para dados fundamentalistas (dado trimestral válido até próxima publicação)

**Winsorização:** Para mitigar efeito de outliers extremos, retornos são *winsorizados* nos percentis 1 e 99 em análises de robustez.

### Justificativa do Período

A escolha do período Janeiro/2016 a Novembro/2025 justifica-se por:

1. **Ponto de inflexão institucional:** 2016 marca o início do período pós-Lava Jato, com reestruturação de governança na Petrobras e novo regime de gestão. 

2. **Cobertura de ciclos:** O período abrange ciclo completo de preços de petróleo (colapso 2015-2016, recuperação 2017-2019, choque COVID 2020, alta 2021-2022, normalização 2023-2025).

3. **Eventos estruturais:** Inclui eventos relevantes para teste da hipótese — pandemia, transição energética, autorização da Margem Equatorial.

4. **Tamanho amostral:** Aproximadamente 2.460 observações diárias fornecem poder estatístico adequado para estimação de múltiplos parâmetros. 

---

## Reprodutibilidade Computacional

A reprodutibilidade constitui princípio metodológico central deste trabalho.  Seguindo o paradigma de pesquisa computacional reproduzível [@buckheitWaveLab1995], todos os dados, procedimentos analíticos e rotinas de geração de resultados estão disponíveis em repositório público:

> **Repositório:** [https://github.com/lcfranca/unb-cca-mqac](https://github. com/lcfranca/unb-cca-mqac)

### Estrutura do Repositório

O repositório organiza-se segundo princípios de separação de responsabilidades:

```
unb-cca-mqac/
+-- data/
|   +-- raw/              # Dados brutos (não processados)
|   +-- processed/        # Dados processados
|   +-- outputs/          # Resultados gerados
|       +-- tables/       # Tabelas em formato LaTeX
|       +-- figures/      # Figuras em formato PDF
+-- src/                  # Código-fonte Python
|   +-- gen_capm.py       # Estimação CAPM
|   +-- gen_qval_scoring.py    # Motor Q-VAL
|   +-- gen_regression_analysis.py  # Análise de regressões
|   +-- utils/            # Funções auxiliares
+-- content/              # Conteúdo textual (Markdown/LaTeX)
+-- notebooks/            # Jupyter notebooks exploratórios
+-- Makefile              # Automação de execução
```

### Princípios de Reprodutibilidade

**Separação Dados-Código-Resultados:** Dados brutos são armazenados separadamente do código de processamento e dos outputs derivados. Esta separação permite:
- Verificação independente dos procedimentos
- Atualização de dados sem modificação de código
- Rastreabilidade completa do pipeline analítico

**Versionamento:** Todo código é versionado via Git, com histórico completo de modificações.  Cada resultado pode ser rastreado à versão específica do código que o gerou.

**Ambiente Computacional:** Dependências são especificadas em arquivo `requirements.txt`, garantindo que o ambiente computacional possa ser recriado.  Versões específicas de bibliotecas são fixadas para evitar quebras por atualizações. 

**Execução Automatizada:** O `Makefile` na raiz do repositório permite execução completa do pipeline analítico via comando único:

```bash
make all
```

Este comando executa sequencialmente:
1.  Coleta e processamento de dados
2.  Estimação de modelos
3. Geração de tabelas e figuras
4. Compilação do documento final

### Verificação Independente

Pesquisadores interessados em verificar ou estender os resultados podem:

1.  Clonar o repositório: `git clone https://github.com/lcfranca/unb-cca-mqac.git`
2. Instalar dependências: `pip install -r requirements. txt`
3.  Executar pipeline: `make all`
4. Comparar outputs gerados com os reportados no documento

A transparência metodológica permite que usuários ajustem parâmetros (pesos do Q-VAL, período amostral, métricas incluídas), verifiquem robustez, e adaptem os modelos a novos contextos ou ativos.

---

## Síntese Metodológica

A metodologia apresentada operacionaliza a pergunta teórica — *métricas fundamentalistas adicionam informação ao mecanismo de preços? * — em procedimento empírico testável. O diagrama abaixo sintetiza o fluxo analítico:

```
+-----------------+     +------------------+     +-----------------+
|  Dados Brutos   |---->|   Processamento  |---->|  Motor Q-VAL    |
|  (Preços, DFs)  |     |  (Normalização)  |     |  (Score 0-100)  |
+-----------------+     +------------------+     +--------+--------+
                                                         |
                                                         V
+-----------------+     +------------------+     +-----------------+
|   Comparação    |<----|    Regressões    |<----| Série Temporal  |
|   de Modelos    |     |   (M0->M1->M2->M3)|     |   de Scores     |
+--------+--------+     +------------------+     +-----------------+
         |
         V
+-----------------------------------------------------------------+
|                    Métricas de Avaliação                        |
|  * Delta R2 (contribuição informacional)                        |
|  * AIC/BIC (parcimônia vs. explicação)                          |
|  * Testes F/t (significância estatística)                       |
|  * R2 out-of-sample (poder preditivo genuíno)                   |
+-----------------------------------------------------------------+
```

Os resultados desta análise permitirão conclusões sobre:

1. **Magnitude da contribuição:** Qual o $\Delta R^2$ atribuível às métricas fundamentalistas?
2.  **Significância estatística:** A contribuição é estatisticamente distinguível de zero?
3. **Relevância econômica:** A contribuição traduz-se em capacidade preditiva operacional? 
4. **Estabilidade temporal:** A contribuição é estável ou varia entre regimes? 
5. **Parcimônia:** O ganho explicativo justifica a complexidade adicional? 

As respostas a estas questões informarão a discussão teórica sobre eficiência informacional do mercado brasileiro com respeito a informação fundamentalista pública — contribuindo para o debate entre visões hayekiana, EMH, Grossman-Stiglitz e mercados adaptativos, com foco empírico no caso Petrobras. 

# Resultados

# Discussão

# Conclusão



# Referências {.unnumbered}

::: {#refs}
:::
