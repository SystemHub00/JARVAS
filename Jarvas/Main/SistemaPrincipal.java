import LEADS.InvestidorDeSucesso;
import TAREFAS.CadastrarAPP;
import TAREFAS.IncluirEmTurma;
import TAREFAS.AlterarNumeroDoContrato;
import TAREFAS.AlterarNomeDoCurso;
import FERRAMENTAS.AcharCoordenadas;
import java.awt.event.ActionListener;
import java.io.PrintStream;
import java.io.OutputStream;
import javax.swing.*;
import java.awt.*;

public class SistemaPrincipal extends JFrame {
    private Thread automacaoThread;

    /**
     * Inicia uma automação em uma nova thread, garantindo que apenas uma automação rode por vez.
     * Se já houver uma automação rodando, exibe mensagem e não inicia outra.
     * @param automacao Runnable com o código da automação
     */
    private void iniciarAutomacao(Runnable automacao) {
        if (automacaoThread != null && automacaoThread.isAlive()) {
            System.out.println("Já existe uma automação em execução. Pare antes de iniciar outra.");
            return;
        }
        automacaoThread = new Thread(() -> {
            try {
                automacao.run();
            } catch (Exception e) {
                System.out.println("Erro na automação: " + e.getMessage());
            }
        });
        automacaoThread.start();
    }
    
    public SistemaPrincipal() {
        // ...existing code...
        setTitle("AI - JARVAS");
        setSize(600, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        getContentPane().setBackground(new Color(18, 18, 30));
        setLayout(new GridBagLayout());

        JPanel panel = new JPanel();
        panel.setBackground(new Color(28, 28, 48));
        panel.setLayout(new GridBagLayout());

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.insets = new Insets(10, 0, 10, 0);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        JLabel label = new JLabel("AI - JARVAS");
        label.setFont(new Font("Orbitron", Font.BOLD, 28));
        label.setForeground(new Color(255, 0, 80));
        label.setHorizontalAlignment(SwingConstants.CENTER);
        label.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createMatteBorder(0, 0, 4, 0, new Color(255, 0, 80)),
            BorderFactory.createEmptyBorder(20, 10, 20, 10)));
        gbc.gridwidth = 1;
        panel.add(label, gbc);

        // Botão seta para expandir/recolher
        gbc.gridy++;
        JButton btnExpandir = new JButton("▼ Automação");
        btnExpandir.setFont(new Font("Orbitron", Font.BOLD, 18));
        btnExpandir.setBackground(new Color(30, 30, 60));
        btnExpandir.setForeground(new Color(255, 255, 255));
        btnExpandir.setFocusPainted(false);
        btnExpandir.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createBevelBorder(1, new Color(255,0,80), new Color(80,0,255)),
            BorderFactory.createEmptyBorder(10, 32, 10, 32)));
        btnExpandir.setCursor(new Cursor(Cursor.HAND_CURSOR));
        panel.add(btnExpandir, gbc);

        // Painel de botões de automação (inicialmente oculto)
        gbc.gridy++;
        JPanel botoesPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 8, 8));
        botoesPanel.setBackground(new Color(28, 28, 48));



        JButton btnInvestidorPeq = criarBotaoPequeno("Investidor");
        btnInvestidorPeq.addActionListener(e -> iniciarAutomacao(() -> InvestidorDeSucesso.executarInvestidorDeSucesso()));
        botoesPanel.add(btnInvestidorPeq);

        JButton btnCadastrarAppPeq = criarBotaoPequeno("Cadastrar APP");
        btnCadastrarAppPeq.addActionListener(e -> iniciarAutomacao(() -> CadastrarAPP.executarCadastrarAPP()));
        botoesPanel.add(btnCadastrarAppPeq);

        JButton btnIncluirTurmaPeq = criarBotaoPequeno("Incluir Turma");
        btnIncluirTurmaPeq.addActionListener(e -> iniciarAutomacao(() -> IncluirEmTurma.executarIncluirTurma()));
        botoesPanel.add(btnIncluirTurmaPeq);

        JButton btnAlterarContratoPeq = criarBotaoPequeno("Alterar Contrato");
        btnAlterarContratoPeq.addActionListener(e -> iniciarAutomacao(() -> AlterarNumeroDoContrato.executarMudarContrato()));
        botoesPanel.add(btnAlterarContratoPeq);

        JButton btnAlterarNomeCursoPeq = criarBotaoPequeno("Alterar Curso");
        btnAlterarNomeCursoPeq.addActionListener(e -> iniciarAutomacao(() -> AlterarNomeDoCurso.executarBotCurso()));
        botoesPanel.add(btnAlterarNomeCursoPeq);

        JButton btnAcharCoordenadasPeq = criarBotaoPequeno("Coordenadas");
        btnAcharCoordenadasPeq.addActionListener(e -> iniciarAutomacao(() -> AcharCoordenadas.main(new String[]{})));
        botoesPanel.add(btnAcharCoordenadasPeq);

        // Botão Stop
        JButton btnStop = criarBotaoPequeno("Stop");
        btnStop.setBackground(new Color(255, 0, 80));
        btnStop.setForeground(Color.WHITE);
        btnStop.addActionListener(e -> {
            if (automacaoThread != null && automacaoThread.isAlive()) {
                automacaoThread.interrupt();
                System.out.println("[STOP] - Automação interrompida!");
            } else {
                System.out.println("Nenhuma automação em execução.");
            }
        });
        botoesPanel.add(btnStop);

        botoesPanel.setVisible(false);
        panel.add(botoesPanel, gbc);

        // Botão seta mostra/oculta painel de botões
        btnExpandir.addActionListener(e -> {
            boolean mostrar = !botoesPanel.isVisible();
            botoesPanel.setVisible(mostrar);
            btnExpandir.setText(mostrar ? "▲ Automação" : "▼ Automação");
            panel.revalidate();
        });

        // Painel de terminal (área de saída)
        gbc.gridy++;
        JTextArea terminalArea = new JTextArea(8, 40);
        terminalArea.setEditable(false);
        terminalArea.setFont(new Font("Consolas", Font.PLAIN, 14));
        terminalArea.setBackground(new Color(18, 18, 30));
        terminalArea.setForeground(new Color(0, 255, 0));
        JScrollPane terminalScroll = new JScrollPane(terminalArea);
        terminalScroll.setBorder(BorderFactory.createTitledBorder(BorderFactory.createLineBorder(new Color(255,0,80)), "Terminal", 0, 0, new Font("Arial", Font.BOLD, 14), new Color(255,0,80)));
        panel.add(terminalScroll, gbc);

        // Redireciona System.out para o terminalArea
        PrintStream printStream = new PrintStream(new OutputStream() {
            @Override
            public void write(int b) {
                terminalArea.append(String.valueOf((char) b));
                terminalArea.setCaretPosition(terminalArea.getDocument().getLength());
            }
        });
        System.setOut(printStream);
        System.setErr(printStream);

        // Centraliza o painel na janela
        GridBagConstraints mainGbc = new GridBagConstraints();
        mainGbc.gridx = 0;
        mainGbc.gridy = 0;
        mainGbc.anchor = GridBagConstraints.CENTER;
        add(panel, mainGbc);

        setVisible(true);
    }


    private JButton criarBotao(String texto) {
        JButton botao = new JButton(texto);
        botao.setFont(new Font("Orbitron", Font.BOLD, 18));
        botao.setBackground(new Color(30, 30, 60));
        botao.setForeground(new Color(255, 255, 255));
        botao.setFocusPainted(false);
        botao.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createBevelBorder(1, new Color(255,0,80), new Color(80,0,255)),
            BorderFactory.createEmptyBorder(16, 32, 16, 32)));
        botao.setCursor(new Cursor(Cursor.HAND_CURSOR));
        botao.setContentAreaFilled(true);
        botao.setOpaque(true);
        botao.setRolloverEnabled(true);
        botao.addChangeListener(e -> {
            if (botao.getModel().isRollover()) {
                botao.setBackground(new Color(255, 0, 80));
                botao.setForeground(Color.BLACK);
            } else {
                botao.setBackground(new Color(30, 30, 60));
                botao.setForeground(Color.WHITE);
            }
        });
        return botao;
    }

    // Cria botões pequenos para o painel horizontal
    private JButton criarBotaoPequeno(String texto) {
        JButton botao = new JButton(texto);
        botao.setFont(new Font("Arial", Font.BOLD, 13));
        botao.setBackground(new Color(30, 30, 60));
        botao.setForeground(new Color(255, 255, 255));
        botao.setFocusPainted(false);
        botao.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createBevelBorder(1, new Color(255,0,80), new Color(80,0,255)),
            BorderFactory.createEmptyBorder(6, 12, 6, 12)));
        botao.setCursor(new Cursor(Cursor.HAND_CURSOR));
        botao.setContentAreaFilled(true);
        botao.setOpaque(true);
        botao.setRolloverEnabled(true);
        botao.addChangeListener(e -> {
            if (botao.getModel().isRollover()) {
                botao.setBackground(new Color(255, 0, 80));
                botao.setForeground(Color.BLACK);
            } else {
                botao.setBackground(new Color(30, 30, 60));
                botao.setForeground(Color.WHITE);
            }
        });
        return botao;
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