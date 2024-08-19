export default function handler(req, res) {
    if (req.method === 'POST') {
      const { email, password } = req.body;
  
      // Verificação básica das credenciais
      if (email === 'user' && password === 'password') {
        res.status(200).json({ message: 'Login bem-sucedido' });
      } else {
        res.status(401).json({ message: 'Credenciais inválidas' });
      }
    } else {
      res.status(405).end(); // Método não permitido
    }
  }
  