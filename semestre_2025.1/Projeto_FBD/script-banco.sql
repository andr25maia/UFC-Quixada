--drop table assistente_social cascade;
--drop table acompanha;
--drop table assistente_interacao;
--drop table beneficio_solicitacao;
--drop table monitora;
--drop table assistente_social_area_atuacao;
--drop table assistente_avalia;
--drop table assistente_social_funcao;
--drop table funcao;
--drop table denuncia;
--drop table assistente_participa;
--drop table familia cascade;
--drop table beneficio cascade;
--drop table beneficio_data_recebimento;
--drop table beneficio_condicoes;
--drop table beneficio_acre_valor;
--drop table beneficio_data_atua;
--drop table recebe;
--drop table projeto cascade;
--drop table projeto_condicoes;
--drop table projeto_area_atuacao;
--drop table membro cascade;
--drop table pessoa_vacinas;
--drop table estudante;
--drop table membro_participa;

CREATE TABLE assistente_social
(
  pnome VARCHAR(20) NOT NULL,
  sobrenome VARCHAR(20) NOT NULL,
  CPF SERIAL,
  senha VARCHAR(10) NOT NULL,
  PRIMARY KEY (CPF)
);

CREATE TABLE beneficio
(
  cod_beneficio SERIAL,
  valor INT NOT NULL,
  data_inicio DATE NOT NULL,
  data_fim DATE,
  nome VARCHAR(100) NOT NULL,
  PRIMARY KEY (cod_beneficio)
);

CREATE TABLE projeto
(
  id SERIAL,
  nome VARCHAR(50) NOT NULL,
  descricao VARCHAR(200) NOT NULL,
  data_inicio DATE NOT NULL,
  data_fim DATE,
  status INT NOT NULL,
  CPF_ass_responsavel INT NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE assistente_participa
(
  funcao VARCHAR(50) NOT NULL,
  data_inicio DATE NOT NULL,
  data_fim DATE NOT NULL,
  CPF INT NOT NULL,
  id SERIAL,
  PRIMARY KEY (CPF, id)

);

CREATE TABLE monitora
(
  CPF INT NOT NULL,
  cod_beneficio INT NOT NULL,
  PRIMARY KEY (CPF, cod_beneficio)
);

CREATE TABLE assistente_social_area_atuacao
(
  area_atuacao VARCHAR(50) NOT NULL,
  CPF INT NOT NULL,
  PRIMARY KEY (area_atuacao, CPF)
);

CREATE TABLE beneficio_acre_valor
(
  acre_valor INT NOT NULL,
  cod_beneficio INT NOT NULL,
  PRIMARY KEY (acre_valor, cod_beneficio)
);

CREATE TABLE beneficio_condicoes
(
  condicoes VARCHAR(50) NOT NULL,
  cod_beneficio INT NOT NULL,
  PRIMARY KEY (condicoes, cod_beneficio)
);

CREATE TABLE beneficio_data_atua
(
  data_atua DATE NOT NULL,
  cod_beneficio INT NOT NULL,
  PRIMARY KEY (data_atua, cod_beneficio)
);

CREATE TABLE beneficio_data_recebimento
(
  data_recebimento_ DATE NOT NULL,
  cod_beneficio INT NOT NULL,
  PRIMARY KEY (data_recebimento_, cod_beneficio)
);

CREATE TABLE projeto_condicoes
(
  condicoes VARCHAR(50) NOT NULL,
  id INT NOT NULL,
  PRIMARY KEY (condicoes, id)
);

CREATE TABLE projeto_area_atuacao
(
  area_atuacao VARCHAR(50) NOT NULL,
  id INT NOT NULL,
  PRIMARY KEY (area_atuacao, id)
);

CREATE TABLE funcao
(
  id_funcao INT NOT NULL,
  nome_funcao VARCHAR(100) NOT NULL,
  PRIMARY KEY (id_funcao)
);

CREATE TABLE assistente_social_funcao
(
  CPF INT NOT NULL,
  id_funcao INT NOT NULL,
  PRIMARY KEY (CPF, id_funcao)
);

CREATE TABLE familia
(
  estado VARCHAR(50) NOT NULL,
  cidade VARCHAR(50) NOT NULL,
  regiao VARCHAR(50) NOT NULL,
  CEP NUMERIC(8) NOT NULL,
  rua VARCHAR(50) NOT NULL,
  numero NUMERIC(5) NOT NULL,
  cod_familia SERIAL,
  pontuacao_vulnerabilidade INT NOT NULL,
  renda_per_capita INT NOT NULL,
  bairro VARCHAR(50) NOT NULL,
  nis_responsavel INT NOT NULL,
  PRIMARY KEY (cod_familia),
  UNIQUE (nis_responsavel),
  UNIQUE (estado, cidade, regiao, CEP, rua, numero, bairro)
);

CREATE TABLE membro
(
  genero VARCHAR(20) NOT NULL,
  nis SERIAL,
  CPF NUMERIC(11) NOT NULL,
  status_emprego INT NOT NULL,
  escolaridade VARCHAR(30) NOT NULL,
  etnia VARCHAR(30) NOT NULL,
  renda_mensal INT NOT NULL,
  tem_filho INT NOT NULL,
  parentesco_resp VARCHAR(50) NOT NULL,
  eh_gestante INT NOT NULL,
  nome VARCHAR(20) NOT NULL,
  responsavel_nis INT NOT NULL,
  PRIMARY KEY (nis)
);

CREATE TABLE estudante
(
  nome_escola VARCHAR(100) NOT NULL,
  tipo_escola VARCHAR(50) NOT NULL,
  assituidade INT NOT NULL,
  media INT NOT NULL,
  nis INT NOT NULL,
  PRIMARY KEY (nis)
);

CREATE TABLE acompanha
(
  cod_familia INT NOT NULL,
  CPF INT NOT NULL,
  PRIMARY KEY (cod_familia, CPF)
);

CREATE TABLE assistente_interacao
(
  data DATE NOT NULL,
  hora VARCHAR(6) NOT NULL,
  observacoes VARCHAR(100) NOT NULL,
  tipo_interacao VARCHAR(100) NOT NULL,
  CPF INT NOT NULL,
  cod_familia INT NOT NULL,
  PRIMARY KEY (CPF, cod_familia)
);

CREATE TABLE membro_participa
(
  data_inicio DATE NOT NULL,
  data_fim DATE NOT NULL,
  status INT NOT NULL,
  id INT NOT NULL,
  nis_participante INT NOT NULL,
  PRIMARY KEY (id, nis_participante)
);

CREATE TABLE assistente_avalia
(
  data DATE NOT NULL,
  proxima_avaliacao INT NOT NULL,
  nova_pont INT NOT NULL,
  CPF INT NOT NULL,
  cod_familia INT NOT NULL,
  PRIMARY KEY (CPF, cod_familia)
);

CREATE TABLE beneficio_solicitacao
(
  status INT NOT NULL,
  justificativa VARCHAR(500),
  cod_beneficio INT NOT NULL,
  cod_familia INT NOT NULL,
  cpf_assistente INT NOT NULL,
  PRIMARY KEY (cod_beneficio, cod_familia)
);

CREATE TABLE recebe
(
  data_inicio DATE NOT NULL,
  data_fim DATE NOT NULL,
  valor_recebido INT NOT NULL,
  cod_beneficio INT NOT NULL,
  cod_familia INT NOT NULL,
  PRIMARY KEY (cod_beneficio, cod_familia)
);

CREATE TABLE pessoa_vacinas
(
  id_vacina INT NOT NULL,
  nome_vacina VARCHAR(100) NOT NULL,
  data_aplicacao DATE NOT NULL,
  nis_membro INT NOT NULL,
  PRIMARY KEY (id_vacina, nis_membro)
);

CREATE TABLE denuncia
(
  id_denuncia SERIAL,
  descricao VARCHAR(500) NOT NULL,
  data_registro DATE NOT NULL,
  observacoes VARCHAR(250) NOT NULL,
  status INT NOT NULL,
  CPF_assistente INT NOT NULL,
  cod_familia INT NOT NULL,
  PRIMARY KEY (id_denuncia)
);

-- Inserindo fk no assistente_participa
alter table assistente_participa add constraint fk_id_projeto foreign key (id) references Projeto(id);
alter table assistente_participa add constraint fk_cpf_assiste foreign key (cpf) references assistente_social(cpf);

-- Inserindo fk no projeto
alter table projeto add constraint fk_cpf_responsavel foreign key (cpf_ass_responsavel) references assistente_social(cpf);

-- Inserindo fk no projeto_condicoes
alter table projeto_condicoes add constraint fk_id_projeto foreign key(id) references projeto(id);

-- Inserindo fk no projeto_area_atuacao
alter table projeto_area_atuacao add constraint fk_id_projeto foreign key(id) references projeto(id);

-- Inserindo fk no membro_participa
alter table membro_participa add constraint fk_id_projeto foreign key(id) references projeto(id);
alter table membro_participa add constraint fk_nis_membro foreign key(nis_participante) references membro(nis);

-- Inserindo fk no membro
alter table membro add constraint fk_responsavel_nis foreign key(responsavel_nis) references membro(nis);

-- Inserindo fk na pessoa_vacinas
alter table pessoa_vacinas add constraint fk_nis_membro foreign key(nis_membro) references membro(nis);

-- Inserindo fk no estudante
alter table estudante add constraint fk_nis_membro foreign key(nis) references membro(nis);

-- Inserindo fk na familia
alter table familia add constraint fk_nis_responsavel foreign key(nis_responsavel) references membro(nis);

-- Inserindo fk nas tabelas derivadas de beneficio
alter table beneficio_data_recebimento add constraint fk_cod_beneficio foreign key(cod_beneficio) references beneficio(cod_beneficio);
alter table beneficio_condicoes add constraint fk_cod_beneficio foreign key(cod_beneficio) references beneficio(cod_beneficio);
alter table beneficio_acre_valor add constraint fk_cod_beneficio foreign key(cod_beneficio) references beneficio(cod_beneficio);
alter table beneficio_data_atua add constraint fk_cod_beneficio foreign key(cod_beneficio) references beneficio(cod_beneficio);

-- Inserindo fk na tabela recebe
alter table recebe add constraint fk_cod_beneficio foreign key(cod_beneficio) references beneficio(cod_beneficio);
alter table recebe add constraint fk_cod_familia foreign key(cod_familia) references familia(cod_familia);

-- Inserindo fk na acompanha
alter table acompanha add constraint fk_cod_familia foreign key(cod_familia) references familia(cod_familia);
alter table acompanha add constraint fk_cpf_assistente foreign key(cpf) references assistente_social(cpf);

-- Inserindo fk na assistente_interacao
alter table assistente_interacao add constraint fk_cod_familia foreign key(cod_familia) references familia(cod_familia);
alter table assistente_interacao add constraint fk_cpf_assistente foreign key(cpf) references assistente_social(cpf);

-- Inserindo fk na beneficio_solicitacao
alter table beneficio_solicitacao add constraint fk_cod_beneficio foreign key(cod_beneficio) references beneficio(cod_beneficio);
alter table beneficio_solicitacao add constraint fk_cod_familia foreign key(cod_familia) references familia(cod_familia);
alter table beneficio_solicitacao add constraint fk_cpf_assistente foreign key(cpf_assistente) references assistente_social(cpf);
-- Inserindo fk na monitora
alter table monitora add constraint fk_cpf_assistente foreign key(cpf) references assistente_social(cpf);
alter table monitora add constraint fk_cod_beneficio foreign key(cod_beneficio) references beneficio(cod_beneficio);

-- Inserindo fk na assistente_Social_area_atuacao
alter table assistente_social_area_atuacao add constraint fk_cpf_assistente foreign key(cpf) references assistente_social(cpf);

-- Inserindo fk na assistente_avalia
alter table assistente_avalia add constraint fk_cpf_assistente foreign key(cpf) references assistente_social(cpf);
alter table assistente_avalia add constraint fk_cod_familia foreign key(cod_familia) references familia(cod_familia);

-- Inserindo fk na assistente_social_funcao
alter table assistente_social_funcao add constraint fk_cpf_assistente foreign key(cpf) references assistente_social(cpf);
alter table assistente_social_funcao add constraint fk_id_funcao foreign key(id_funcao) references funcao(id_funcao);

-- Inserindo fk na Denuncia
alter table denuncia add constraint fk_cpf_assistente foreign key(cpf_assistente) references assistente_social(cpf);
alter table denuncia add constraint fk_cod_familia foreign key(cod_familia) references familia(cod_familia);