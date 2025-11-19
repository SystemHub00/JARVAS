import javax.swing.*;
import java.awt.*;

public class SistemaPrincipal extends JFrame {
    
    public SistemaPrincipal() {
        // Configurações básicas do JFrame
        setTitle("Minha Primeira Interface");  // Título da janela
        setSize(400, 300);                     // Largura x Altura
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); // Fechar aplicação ao clicar X
        setLocationRelativeTo(null);           // Centralizar na tela
        setLayout(new FlowLayout());           // Gerenciador de layout
        
        // Criando componentes
        JLabel label = new JLabel("Olá, Jarvas");
        JButton botao = new JButton("Clique Aqui");
        JTextField campoTexto = new JTextField(15);
        
        // Adicionando componentes ao JFrame
        add(label);
        add(campoTexto);
        add(botao);
        
        // Tornar a janela visível
        setVisible(true);
    }
    
    public static void main(String[] args) {
        // Criar a interface na Event Dispatch Thread
        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                new SistemaPrincipal();
            }
        });
    }
}
