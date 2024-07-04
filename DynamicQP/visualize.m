function visualize(output)
    x1 = linspace(-2*pi,2*pi,50);
    x2 = linspace(-2*pi,2*pi,50);
    [X1,X2] = meshgrid(x1,x2);
    
    figure('Position', [560,140,800,800]);hold on;
    % caxis([-3,3])
    N = numel(output.tout);
    max_frames = 200;
    for i=1:floor(N/max_frames):N
        t = output.tout(i);
        cla;hold on;
        f = (sin(t)/4 + 1)*X1.^2 + (cos(t)/4 + 1)*X2.^2 + cos(t)*X1.*X2 + sin(3*t)*X1 + cos(3*t)*X2;
        cnt_x2 = (cos(2*t) - sin(4*t)*x1) / cos(4*t);
        contourf(X1, X2, f, '--');
        plot(x1, cnt_x2, 'r', 'LineWidth', 5);
        scatter(output.y.Data(i,1), output.y.Data(i,2), 50, ...
            'MarkerFaceColor', 'k', 'LineWidth', 2, 'MarkerEdgeColor', 'y');
        axis([-2*pi,2*pi,-2*pi,2*pi])
        caxis([0,150])
        colorbar;
        drawnow limitrate;
    end
end