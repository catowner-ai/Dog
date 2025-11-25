package J1120;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.net.*;
import javax.imageio.ImageIO;
import java.util.*;

public class J1120_poke {
    public static void main(String[] args) {
        System.out.println("正在召喚皮卡丘……皮卡皮卡～");
        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (Exception ignored) {}
            new PokemonMinesweeper().setVisible(true);
        });
    }
}

class PokemonMinesweeper extends JFrame {
    private int rows = 9, cols = 9, mines = 10;
    private JButton[][] buttons;
    private int[][] board;
    private boolean[][] revealed, flagged;
    private boolean firstClick = true, gameOver = false;
    private int flagsLeft, seconds = 0;

    private JLabel mineLabel, timeLabel, statusLabel;
    private JPanel topPanel;           // ← 這裡改成成員變數，restart 才找得到！
    private javax.swing.Timer timer;

    public PokemonMinesweeper() {
        setTitle("寶可夢地雷王 - 最終穩定版");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        createTopPanel();              // 先建立上方面板
        add(topPanel, BorderLayout.NORTH);

        restart();                     // 開始遊戲
        pack();
        setLocationRelativeTo(null);
        setResizable(false);
    }

    private void createTopPanel() {
        topPanel = new JPanel();
        topPanel.setBackground(new Color(255, 182, 193));
        topPanel.setBorder(BorderFactory.createEmptyBorder(10,10,10,10));

        mineLabel = new JLabel("地雷: 10");
        mineLabel.setFont(new Font("微軟正黑體", Font.BOLD, 20));
        timeLabel = new JLabel("000");
        timeLabel.setFont(new Font("Consolas", Font.BOLD, 32));
        timeLabel.setForeground(Color.RED);
        statusLabel = new JLabel("點擊開始遊戲，第一下絕對安全！");

        JButton face = new JButton("皮卡丘");
        face.setFont(new Font("微軟正黑體", Font.BOLD, 24));
        face.addActionListener(e -> restart());

        String[] levels = {"新手 9×9 10雷", "中級 16×16 40雷", "高手 16×30 99雷"};
        JComboBox<String> levelBox = new JComboBox<>(levels);
        levelBox.addActionListener(e -> {
            int idx = levelBox.getSelectedIndex();
            rows = idx == 0 ? 9 : 16;
            cols = idx == 2 ? 30 : (idx == 0 ? 9 : 16);
            mines = idx == 0 ? 10 : idx == 1 ? 40 : 99;
            restart();
        });

        topPanel.add(new JLabel("難度：")); 
        topPanel.add(levelBox);
        topPanel.add(Box.createHorizontalStrut(30));
        topPanel.add(mineLabel); 
        topPanel.add(Box.createHorizontalStrut(40));
        topPanel.add(face); 
        topPanel.add(Box.createHorizontalStrut(40));
        topPanel.add(timeLabel); 
        topPanel.add(Box.createHorizontalStrut(30));
        topPanel.add(statusLabel);
    }

    private void restart() {
        firstClick = true; gameOver = false; seconds = 0; flagsLeft = mines;
        mineLabel.setText("地雷: " + mines);
        timeLabel.setText("000");
        statusLabel.setText("新遊戲！第一下絕對不會死！");
        if (timer != null) timer.stop();
        timer = new javax.swing.Timer(1000, e -> timeLabel.setText(String.format("%03d", ++seconds)));

        // 清除舊棋盤
        Container c = getContentPane();
        if (c.getComponentCount() > 1) c.remove(1);
        c.add(createBoard(), BorderLayout.CENTER);

        revalidate();
        repaint();
        pack();
    }

    private JPanel createBoard() {
        JPanel panel = new JPanel(new GridLayout(rows, cols, 1, 1));
        panel.setBackground(Color.BLACK);
        buttons = new JButton[rows][cols];
        board = new int[rows][cols];
        revealed = new boolean[rows][cols];
        flagged = new boolean[rows][cols];

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                JButton b = new JButton();
                b.setPreferredSize(new Dimension(36, 36));
                b.setBackground(new Color(200, 255, 200));
                b.setMargin(new Insets(0,0,0,0));
                b.setBorder(BorderFactory.createRaisedBevelBorder());

                int r = i, c = j;
                b.addMouseListener(new MouseAdapter() {
                    @Override
                    public void mousePressed(MouseEvent e) {
                        if (gameOver || revealed[r][c]) return;

                        if (SwingUtilities.isRightMouseButton(e)) {
                            if (!revealed[r][c]) {
                                flagged[r][c] = !flagged[r][c];
                                b.setIcon(flagged[r][c] ? getFlagIcon() : null);
                                flagsLeft += flagged[r][c] ? -1 : 1;
                                mineLabel.setText("地雷: " + flagsLeft);
                            }
                            return;
                        }

                        if (flagged[r][c]) return;

                        if (firstClick) {
                            firstClick = false;
                            placeMines(r, c);
                            timer.start();
                            statusLabel.setText("遊戲開始！快保護寶可夢！");
                        }

                        if (board[r][c] < 0) {
                            explode(r, c);
                            return;
                        }

                        reveal(r, c);
                        checkWin();
                    }
                });

                buttons[i][j] = b;
                panel.add(b);
            }
        }
        return panel;
    }

    private void placeMines(int er, int ec) {
        Random rand = new Random();
        int placed = 0;
        while (placed < mines) {
            int i = rand.nextInt(rows);
            int j = rand.nextInt(cols);
            if (board[i][j] == 0 && !(Math.abs(i-er)<=1 && Math.abs(j-ec)<=1)) {
                board[i][j] = -(rand.nextInt(1010) + 1);  // 存負的 pokemon id
                placed++;
            }
        }
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                if (board[i][j] == 0)
                    board[i][j] = countMines(i, j);
    }

    private int countMines(int i, int j) {
        int cnt = 0;
        for (int di = -1; di <= 1; di++)
            for (int dj = -1; dj <= 1; dj++)
                if (di != 0 || dj != 0) {
                    int ni = i + di, nj = j + dj;
                    if (ni >= 0 && ni < rows && nj >= 0 && nj < cols && board[ni][nj] < 0)
                        cnt++;
                }
        return cnt;
    }

    private void reveal(int i, int j) {
        if (i < 0 || i >= rows || j < 0 || j >= cols || revealed[i][j] || flagged[i][j]) return;
        revealed[i][j] = true;
        JButton b = buttons[i][j];
        b.setEnabled(false);
        b.setBorder(BorderFactory.createLoweredBevelBorder());

        int val = board[i][j];
        if (val > 0) {
            b.setText(String.valueOf(val));
            b.setForeground(getNumberColor(val));
        } else if (val == 0) {
            b.setBackground(new Color(240, 255, 240));
            for (int di = -1; di <= 1; di++)
                for (int dj = -1; dj <= 1; dj++)
                    reveal(i + di, j + dj);
        }
    }

    private void explode(int r, int c) {
        gameOver = true;
        timer.stop();
        int id = Math.abs(board[r][c]);
        String name = getPokemonName(id);

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (board[i][j] < 0)
                    buttons[i][j].setIcon(getPokemonIcon(Math.abs(board[i][j])));
                buttons[i][j].setEnabled(false);
            }
        }

        JOptionPane.showMessageDialog(this,
            "你踩死了 " + name + "！\n牠被你放生了～\n用時 " + seconds + " 秒",
            "寶可夢被踩爆了！", JOptionPane.ERROR_MESSAGE, getPokemonIcon(id));
    }

    private void checkWin() {
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                if (board[i][j] >= 0 && !revealed[i][j]) return;

        gameOver = true;
        timer.stop();
        JOptionPane.showMessageDialog(this,
            "恭喜過關！\n你保護了 " + (rows*cols-mines) + " 隻寶可夢！\n用時 " + seconds + " 秒",
            "你是最強的訓練家！", JOptionPane.INFORMATION_MESSAGE);
    }

    private ImageIcon getPokemonIcon(int id) {
        try {
            URL url = new URL("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/" + id + ".png");
            Image img = ImageIO.read(url).getScaledInstance(80, 80, Image.SCALE_SMOOTH);
            return new ImageIcon(img);
        } catch (Exception e) {
            return new ImageIcon();
        }
    }

    private ImageIcon getFlagIcon() {
        try {
            URL url = new URL("https://flagcdn.com/48x36/tw.png");
            Image img = ImageIO.read(url).getScaledInstance(28, 28, Image.SCALE_SMOOTH);
            return new ImageIcon(img);
        } catch (Exception e) {
            return null;
        }
    }

    private Color getNumberColor(int n) {
        return switch (n) {
            case 1 -> Color.BLUE;
            case 2 -> new Color(0, 128, 0);
            case 3 -> Color.RED;
            case 4 -> new Color(128, 0, 128);
            case 5 -> new Color(139, 0, 0);
            case 6 -> new Color(0, 139, 139);
            case 7 -> Color.BLACK;
            case 8 -> Color.GRAY;
            default -> Color.BLACK;
        };
    }

    private String getPokemonName(int id) {
        return switch (id) {
            case 25 -> "皮卡丘"; case 150 -> "超夢"; case 143 -> "卡比獸";
            case 6 -> "噴火龍"; case 94 -> "耿鬼"; case 445 -> "烈咬陸鯊";
            case 382 -> "蓋歐卡"; case 383 -> "固拉多"; case 384 -> "烈空坐";
            case 483 -> "帝牙盧卡"; case 484 -> "帕路奇亞"; case 487 -> "騎拉帝納";
            case 643 -> "萊希拉姆"; case 644 -> "捷克羅姆"; case 646 -> "酋雷姆";
            case 716 -> "哲爾尼亞斯"; case 717 -> "伊裴爾塔爾"; case 721 -> "火神蛾";
            default -> "第" + id + "號寶可夢";
        };
    }
}

   