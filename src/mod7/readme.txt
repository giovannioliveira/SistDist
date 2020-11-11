instruções para executar:
1) executar node.py
2) executar em outras janelas um ou mais clientes para interagir com as réplicas
3) inserir comandos no cliente:
    3.1) get PORT -> retorna valor da variável na réplica PORT
    3.2) set PORT VALUE -> bloqueia até que consiga obter chapéu em réplica PORT e escreva localmente VALUE
    3.3) publish PORT -> publica último valor publicado na réplica PORT e libera "chapéu"
    3.4) history PORT -> exibe histórico local de alterações com as publicações de outros nós

* a porta inicial e o número de nós são configuráveis. da forma como está, valores de PORT vão de 47123 a 47126