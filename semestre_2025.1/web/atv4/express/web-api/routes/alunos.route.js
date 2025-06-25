var express = require('express');
var router = express.Router();

// Importe o AlunoService se ainda não estiver importado
var AlunoService = require('../services/aluno.service'); // ajuste o caminho conforme a estrutura do seu projeto

// Corrigido: res.json em vez de response.json
router.get("/listar", (req, res, next) => {
    res.json(AlunoService.listar());
});

router.get('/', (req, res) => {
  res.json({ message: 'Alunos funcionando!' });
});

router.post('/criar', (req, res) => {
  const aluno = req.body;
  const novoAluno = AlunoService.criar(aluno);
  res.status(201).json(novoAluno);
});
router.put('/atualizar/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const alunoAtualizado = req.body;
  const aluno = AlunoService.atualizar(id, alunoAtualizado);
  if (aluno) {
    res.json(aluno);
  } else {
    res.status(404).json({ message: 'Aluno não encontrado' });
  }
});
router.delete('/excluir/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const sucesso = AlunoService.excluir(id);
  if (sucesso) {
    res.status(204).send();
  } else {
    res.status(404).json({ message: 'Aluno não encontrado' });
  }
});
router.get('/recuperar/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const aluno = AlunoService.recuperar(id);
  if (aluno) {
    res.json(aluno);
  } else {
    res.status(404).json({ message: 'Aluno não encontrado' });
  }
});

module.exports = router;
