package J1120;
import java.util.Random;
import java.util.Scanner;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

/**
 * J1120_地雷 - 2025 豪華終極版踩地雷
 * 功能完整：第一下不死、計時器、剩餘旗幟、表情重新開始、多難度、自訂地圖、Emoji 美化
 */
public class J1120_地雷 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.println("==================================");
        System.out.println("     2025 豪華版踩地雷遊戲");
        System.out.println("==================================");
        System.out.println("1. 新手   (9×9    10 顆地雷)");
        System.out.println("2. 中級   (16×16  40 顆地雷)");
        System.out.println("3. 高手   (16×30  99 顆地雷)");
        System.out.println("4. 地獄   (20×40 200 顆地雷)");
        System.out.println("5. 自訂地圖");
        System.out.print("請選擇難度 (1-5): ");
        
        int choice = 1;
        try {
            choice = sc.nextInt();
        } catch (Exception e) {
            choice = 1;
        }
        
        int rows = 9, cols = 9, mines = 10;
        switch (choice) {
            case 1 -> { rows=9;   cols=9;   mines=10; }
            case 2 -> { rows=16;  cols=16;  mines=40; }
            case 3 -> { rows=16;  cols=30;  mines=99; }
            case 4 -> { rows=20;  cols=40;  mines=200; }
            case 5 -> {
                System.out.println("自訂地圖模式：");
                rows = safeInput(sc, "行數 (5-50): ", 5, 50, 16);
                cols = safeInput(sc, "列數 (5-60): ", 5, 60, 30);
                mines = safeInput(sc, "地雷數 (10-格子數-1): ", 10, rows*cols-1, 99);
            }
            default -> System.out.println("輸入錯誤，啟動新手模式！");
        }
        
        final int r = rows, c = cols, m = mines;
        
        // 啟動 Swing 視窗（一定要在 EDT 執行）
        SwingUtilities.invokeLater(() -> {
            try {
                // 這一行才是正確的！
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (Exception ignored) {}
            new MinesweeperPro(r, c, m).setVisible(true);
        });
    }
    
    private static int safeInput(Scanner sc, String prompt, int min, int max, int def) {
        System.out.print(prompt);
        try {
            int v = sc.nextInt();
            if (v >= min && v <= max) return v;
        } catch (Exception ignored) {}
        System.out.println("輸入無效，使用預設值 " + def);
        return def;
    }
}

// =============================================
// 以下是遊戲本體
// =============================================
class MinesweeperPro extends JFrame {
    private int rows, cols, mines;
    private JButton[][] buttons;
    private int[][] map;           // -1=地雷, 0=空白, 1-8=旁邊雷數
    private boolean[][] revealed, flagged;
    private boolean firstClick = true;
    private boolean gameOver = false;
    private int flagsLeft;
    private JLabel mineLabel, timeLabel;
    private int seconds = 0;
    private Timer timer;
    private JButton smileButton;

    public MinesweeperPro(int rows, int cols, int mines) {
        this.rows = rows;
        this.cols = cols;
        this.mines = mines;
        
        setTitle("2025 豪華踩地雷 - " + rows + "×" + cols + " (" + mines + " 雷)");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        add(createTopPanel(), BorderLayout.NORTH);
        add(createGamePanel(), BorderLayout.CENTER);

        initGame();
        pack();
        setLocationRelativeTo(null);
        setResizable(false);
    }

    private JPanel createTopPanel() {
        JPanel top = new JPanel();
        top.setBackground(new Color(180, 180, 255));
        top.setBorder(BorderFactory.createLoweredBevelBorder());

        mineLabel = new JLabel();
        mineLabel.setFont(new Font("Consolas", Font.BOLD, 24));
        mineLabel.setForeground(Color.RED);

        smileButton = new JButton("😊");
        smileButton.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 36));
        smileButton.setPreferredSize(new Dimension(50, 50));
        smileButton.addActionListener(e -> initGame());

        timeLabel = new JLabel("000");
        timeLabel.setFont(new Font("Consolas", Font.BOLD, 24));
        timeLabel.setForeground(Color.RED);

        top.add(mineLabel);
        top.add(Box.createHorizontalStrut(30));
        top.add(smileButton);
        top.add(Box.createHorizontalStrut(30));
        top.add(timeLabel);
        return top;
    }

    private JPanel createGamePanel() {
        JPanel panel = new JPanel(new GridLayout(rows, cols, 1, 1));
        panel.setBackground(Color.BLACK);
        return panel;
    }

    private void initGame() {
        firstClick = true;
        gameOver = false;
        seconds = 0;
        flagsLeft = mines;
        updateCounters();

        if (timer != null) timer.stop();
        timer = new Timer(1000, e -> {
            seconds++;
            timeLabel.setText(String.format("%03d", seconds));
        });

        Container c = getContentPane();
        c.remove(1);
        JPanel gamePanel = new JPanel(new GridLayout(rows, cols, 1, 1));
        gamePanel.setBackground(Color.BLACK);

        buttons = new JButton[rows][cols];
        map = new int[rows][cols];
        revealed = new boolean[rows][cols];
        flagged = new boolean[rows][cols];

        MouseAdapter ma = new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent e) {
                if (gameOver) return;
                JButton btn = (JButton) e.getSource();
                Point p = findButtonPosition(btn);
                int i = p.y, j = p.x;

                if (SwingUtilities.isRightMouseButton(e)) {
                    if (!revealed[i][j]) {
                        flagged[i][j] = !flagged[i][j];
                        btn.setText(flagged[i][j] ? "🚩" : "");
                        flagsLeft += flagged[i][j] ? -1 : 1;
                        updateCounters();
                        checkWin();
                    }
                } else if (SwingUtilities.isLeftMouseButton(e) && !flagged[i][j]) {
                    if (firstClick) {
                        firstClick = false;
                        placeMines(i, j);
                        timer.start();
                    }
                    if (map[i][j] == -1) {
                        explode();
                    } else {
                        reveal(i, j);
                        checkWin();
                    }
                }
            }
        };

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                JButton btn = new JButton();
                btn.setPreferredSize(new Dimension(30, 30));
                btn.setMargin(new Insets(0,0,0,0));
                btn.setFont(new Font("Arial", Font.BOLD, 18));
                btn.setFocusPainted(false);
                btn.addMouseListener(ma);
                buttons[i][j] = btn;
                gamePanel.add(btn);
            }
        }

        c.add(gamePanel, BorderLayout.CENTER);
        revalidate();
        repaint();
        smileButton.setText("😊");
    }

    private Point findButtonPosition(JButton btn) {
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                if (buttons[i][j] == btn)
                    return new Point(j, i);
        return null;
    }

    private void placeMines(int excludeI, int excludeJ) {
        Random rand = new Random();
        int placed = 0;
        while (placed < mines) {
            int i = rand.nextInt(rows);
            int j = rand.nextInt(cols);
            if (map[i][j] != -1 && !(i == excludeI && j == excludeJ)) {
                map[i][j] = -1;
                placed++;
            }
        }
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                if (map[i][j] != -1)
                    map[i][j] = countMinesAround(i, j);
    }

    private int countMinesAround(int i, int j) {
        int cnt = 0;
        for (int di = -1; di <= 1; di++)
            for (int dj = -1; dj <= 1; dj++)
                if (di != 0 || dj != 0) {
                    int ni = i + di, nj = j + dj;
                    if (ni >= 0 && ni < rows && nj >= 0 && nj < cols && map[ni][nj] == -1)
                        cnt++;
                }
        return cnt;
    }

    private void reveal(int i, int j) {
        if (i < 0 || i >= rows || j < 0 || j >= cols || revealed[i][j] || flagged[i][j]) return;
        revealed[i][j] = true;
        JButton btn = buttons[i][j];
        btn.setEnabled(false);

        if (map[i][j] == -1) {
            btn.setText("💥");
            btn.setBackground(Color.RED);
        } else if (map[i][j] > 0) {
            btn.setText(String.valueOf(map[i][j]));
            btn.setForeground(getColor(map[i][j]));
        } else {
            btn.setBackground(new Color(220, 220, 220));
        }

        if (map[i][j] == 0) {
            for (int di = -1; di <= 1; di++)
                for (int dj = -1; dj <= 1; dj++)
                    reveal(i + di, j + dj);
        }
    }

    private Color getColor(int n) {
        return switch (n) {
            case 1 -> Color.BLUE;
            case 2 -> new Color(0, 130, 0);
            case 3 -> Color.RED;
            case 4 -> new Color(0, 0, 128);
            case 5 -> new Color(128, 0, 0);
            case 6 -> Color.CYAN;
            case 7 -> Color.BLACK;
            case 8 -> Color.GRAY;
            default -> Color.BLACK;
        };
    }

    private void explode() {
        gameOver = true;
        timer.stop();
        smileButton.setText("😵");
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (map[i][j] == -1) {
                    buttons[i][j].setText(flagged[i][j] ? "✓" : "💣");
                    if (!flagged[i][j]) buttons[i][j].setBackground(Color.RED);
                }
                buttons[i][j].setEnabled(false);
            }
        }
        JOptionPane.showMessageDialog(this, "💥 炸死了！再接再厲～", "Game Over", JOptionPane.ERROR_MESSAGE);
    }

    private void checkWin() {
        if (gameOver) return;
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                if (map[i][j] != -1 && !revealed[i][j])
                    return;
        gameOver = true;
        timer.stop();
        smileButton.setText("😎");
        JOptionPane.showMessageDialog(this, "🎉 恭喜過關！你是掃雷之神！\n用時 " + seconds + " 秒", "勝利！", JOptionPane.INFORMATION_MESSAGE);
    }

    private void updateCounters() {
        mineLabel.setText(String.format("%03d", flagsLeft));
    }
}