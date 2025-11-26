package LEADS;
import java.awt.AWTException;
import java.awt.Robot;
import java.awt.event.KeyEvent;
import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.StringSelection;
// import java.awt.datatransfer.DataFlavor; // Removido pois não é utilizado
import java.awt.Toolkit;
import java.security.spec.ECField;  

public class CulturaCarnaval {
    
    private static Robot robot;
    
    public static final String ADERICISMO = "Cultura Carnaval: Híbrido - Adericismo";
    public static final String COSTURA = "Cultura Carnaval: Híbrido - Costura";
    public static final String PASSISTA = "Cultura Carnaval: Híbrido - Passista";
    public static final String PERCUSSAO = "Cultura Carnaval: Híbrido - Percussão";

    static {
        try {
            robot = new Robot();
        } catch (AWTException e) {                      
            e.printStackTrace();                    
        }
    }
    // CHROME
    // F10
    public static void executaCulturaCarnaval() {
        try {
            timeSleep(5000);
            
            for (int i = 0; i < 61; i++) {
                //=========================== BOTÃO ADICIONAR ==================================//
                hotkey(new int[]{KeyEvent.VK_ALT, KeyEvent.VK_O, KeyEvent.VK_I});
                timeSleep(1200);
                
                //============================= ABRIR EXCEL ====================================//
                hotkey(new int[]{KeyEvent.VK_ALT, KeyEvent.VK_TAB}); // Chrome
                timeSleep(1200);
                
                //============================== COPIA CPF =====================================//
                for (int j = 0; j < 2; j++) {
                    hotkey(new int[]{KeyEvent.VK_CONTROL, KeyEvent.VK_C}); // copia o "CPF"
                    timeSleep(1200);
                }
                timeSleep(1200);
                hotkey(new int[]{KeyEvent.VK_ALT, KeyEvent.VK_TAB}); // F10
                timeSleep(1200);
                pressKey(KeyEvent.VK_TAB);
                timeSleep(1200);
                hotkey(new int[]{KeyEvent.VK_CONTROL, KeyEvent.VK_V}); // colar o "CPF" copiado
                timeSleep(1200);
                pressKey(KeyEvent.VK_ENTER);
                timeSleep(1200);
                
                //============================ BOTÃO PROXIMO - 1 ====================================//
                for (int j = 0; j < 17; j++) {
                    pressKey(KeyEvent.VK_TAB);
                }
                timeSleep(1500);
                
                //================================ PARTE - 2 ========================================//
                //================ TIPO DE CONTRATO ===================//  
                tipoDeContrato();
                timeSleep(1200);
                pressKey(KeyEvent.VK_TAB) ;
                timeSleep(1200);
                
                //============ OPÇÃO - DATA DA MATRÍCULA ==============//
                //================================ ESCOLHER MATRÍCULA ======================================//
                matricula();
                timeSleep(1200);
                pressKey(KeyEvent.VK_TAB);
                pressKey(KeyEvent.VK_TAB);                   
                
                //================ OPÇÃO - EVENTO =====================//
                evento();
                timeSleep(1200);
                pressKey(KeyEvent.VK_TAB);
                
                //================= OPÇÃO - CURSO =====================//
                curso();
                timeSleep(1200);
                pressKey(KeyEvent.VK_TAB);
                timeSleep(1200);
                
                //=============== OPÇÃO - ADMINISTRADO =================//
                adm();
                timeSleep(1200);
                pressKey(KeyEvent.VK_TAB);
                
                //=============== OPÇÃO - COORDENADOR =================//
                coordenador();
                timeSleep(1200);
                
                //============================ BOTÃO PROXIMO - 2 ====================================//
                botaoProximo2();
                timeSleep(1200);
                
                //================================ PARTE - 3 ========================================//
                pressKey(KeyEvent.VK_SPACE);
                polo();
                timeSleep(1200);
                
                //============================ BOTÃO GRAVAR ====================================// 
                botaoGravar();
                timeSleep(1200);
                
                //============================================== EXCEL ====================================================//
                hotkey(new int[]{KeyEvent.VK_ALT, KeyEvent.VK_TAB}); // Chrome
                timeSleep(1200);
                
                for (int j = 0; j < 1; j++) {
                    pressKey(KeyEvent.VK_LEFT);
                }
                pressKey(KeyEvent.VK_SPACE);
                timeSleep(1200);
                pressKey(KeyEvent.VK_DOWN);
                
                for (int j = 0; j < 1; j++) {
                    pressKey(KeyEvent.VK_RIGHT); // Voltar para o proximo CPF
                }
                timeSleep(1200);
                hotkey(new int[]{KeyEvent.VK_ALT, KeyEvent.VK_TAB}); // F10
                timeSleep(1200);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }                           
    
    // Métodos auxiliares para simular as funções do Python
    private static void timeSleep(int milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
    
    private static void pressKey(int keyCode) {
        robot.keyPress(keyCode);
        robot.keyRelease(keyCode);
    }

    private static void hotkey(int[] keys) {
        // Pressiona todas as teclas
        for (int key : keys) {
            robot.keyPress(key);
        }
        
        // Libera todas as teclas
        for (int key : keys) {
        
            robot.keyRelease(key);
        }
    }
                                                 
    private static void tipoDeContrato() {
        String tipoDeContrato = "Bolsa";
        writeText(tipoDeContrato);
    }
                            
    private static void matricula() {
        String dataDoUsuario = "24/11/2025";
        for (int i = 0; i < 10; i++) {
                    
            pressKey(KeyEvent.VK_BACK_SPACE);
        }
        writeText(dataDoUsuario);
    }           
    
    private static void evento() {
        String acao = "8 - Cultura Carnaval";
        writeText(acao);
    }
    
    private static void curso() {       
        String curso = PASSISTA;
        if (curso.equals("Cultura Carnaval: Híbrido - Adericismo")) {
            for (int i = 0; i < 19; i++) {
                pressKey(KeyEvent.VK_DOWN);
            }
        } else if (curso.equals("Cultura Carnaval: Híbrido - Costura")) {
            for (int i = 0; i < 20; i++) {
                pressKey(KeyEvent.VK_DOWN);                                                                 
            }
        } else if (curso.equals("Cultura Carnaval: Híbrido - Passista")) {
            for (int i = 0; i < 21; i++) {
                pressKey(KeyEvent.VK_DOWN);
            }
        } else if (curso.equals("Cultura Carnaval: Híbrido - Percussão")) {
            for (int i = 0; i < 22; i++) {
                pressKey(KeyEvent.VK_DOWN);
            }   
        } 
    }

    private static void adm() {                  
        String adm = "Lucas Luan Pereira Vieira";
        writeText(adm);
    }

    private static void coordenador() {
        String coordenador = "Marcus Vinicius Coppola Souto";
        writeText(coordenador);
    }
    
    private static void botaoProximo2() {                    
        for (int i = 0; i < 5; i++) {
            pressKey(KeyEvent.VK_TAB);
        }
    }
    
    private static void polo() {
        for (int         i = 0; i < 2; i++) {
            pressKey(KeyEvent.VK_TAB);                                                                                          
        }
        for (int v =0; v < 3; v++) {
            pressKey(KeyEvent.VK_DOWN);
        }                               
    }

    private static void botaoGravar() {                                         
        for (int i = 0; i < 6; i++) {
            pressKey(KeyEvent.VK_TAB);
        }
        pressKey(KeyEvent.VK_ENTER);
    }
    
    private static void writeText(String text) {
        // Copia o texto para a área de transferência
        StringSelection stringSelection = new StringSelection(text);
        Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
        clipboard.setContents(stringSelection, null);
        
        // Cola o texto usando Ctrl+V
        hotkey(new int[]{KeyEvent.VK_CONTROL, KeyEvent.VK_V});
    }
    
    // Executar apenas se chamado diretamente
    public static void main(String[] args) {
        executaCulturaCarnaval();
    }
}                                           
